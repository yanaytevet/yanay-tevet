import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse

from django.utils import timezone

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from mcp_server.config import (
    ACCESS_TOKEN_LAST_USED_RESOLUTION_SECONDS,
    ACCESS_TOKEN_TTL_SECONDS,
    AUTHORIZATION_CODE_TTL_SECONDS,
    MCP_SCOPE,
    REFRESH_TOKEN_TTL_SECONDS,
)
from mcp_server.models.oauth_access_token import OAuthAccessToken
from mcp_server.models.oauth_authorization_code import OAuthAuthorizationCode
from mcp_server.models.oauth_client import OAuthClient
from mcp_server.models.oauth_refresh_token import OAuthRefreshToken
from mcp_server.schemas.oauth_consent_schemas import OAuthClientInfo, OAuthConsentRequest
from users.models import User

PKCE_METHOD_S256 = 'S256'


class OAuthManager:
    """Mints and validates OAuth codes/tokens for the MCP authorization server.

    Raw secrets are returned to the caller once and never persisted; only SHA-256
    hashes are stored so a database leak does not expose usable tokens.
    """

    @staticmethod
    def hash_secret(raw: str) -> str:
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_secret() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_pkce(code_verifier: str, code_challenge: str, method: str) -> bool:
        """OAuth 2.1 makes PKCE mandatory, and only S256 is accepted ('plain' offers no
        protection against a leaked authorization request)."""
        if not code_verifier or not code_challenge or method != PKCE_METHOD_S256:
            return False
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        expected = base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')
        return secrets.compare_digest(expected, code_challenge)

    @classmethod
    async def create_authorization_code(
        cls,
        client: OAuthClient,
        user: User,
        redirect_uri: str,
        scope: str,
        resource: str,
        code_challenge: str,
        code_challenge_method: str,
    ) -> str:
        raw_code = cls.generate_secret()
        await OAuthAuthorizationCode.objects.acreate(
            code_hash=cls.hash_secret(raw_code),
            client=client,
            user=user,
            redirect_uri=redirect_uri,
            scope=scope,
            resource=resource,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=timezone.now() + timedelta(seconds=AUTHORIZATION_CODE_TTL_SECONDS),
        )
        return raw_code

    @classmethod
    async def consume_authorization_code(cls, raw_code: str) -> OAuthAuthorizationCode | None:
        code = await OAuthAuthorizationCode.objects.filter(
            code_hash=cls.hash_secret(raw_code), used=False, expires_at__gt=timezone.now(),
        ).select_related('client', 'user').afirst()
        if code is None:
            return None
        # Conditional update so two concurrent redemptions of the same code can't both succeed.
        claimed = await OAuthAuthorizationCode.objects.filter(id=code.id, used=False).aupdate(used=True)
        return code if claimed else None

    @classmethod
    async def create_access_token(
        cls, client: OAuthClient, user: User, scope: str, resource: str,
    ) -> tuple[str, datetime]:
        raw_token = cls.generate_secret()
        expires_at = timezone.now() + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)
        await OAuthAccessToken.objects.acreate(
            token_hash=cls.hash_secret(raw_token),
            client=client,
            user=user,
            scope=scope,
            resource=resource,
            expires_at=expires_at,
        )
        return raw_token, expires_at

    @classmethod
    async def create_refresh_token(
        cls, client: OAuthClient, user: User, scope: str, resource: str,
    ) -> str:
        raw_token = cls.generate_secret()
        await OAuthRefreshToken.objects.acreate(
            token_hash=cls.hash_secret(raw_token),
            client=client,
            user=user,
            scope=scope,
            resource=resource,
            expires_at=timezone.now() + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS),
        )
        return raw_token

    @classmethod
    async def consume_refresh_token(cls, raw_token: str) -> OAuthRefreshToken | None:
        """Refresh tokens are single-use (rotated on every refresh)."""
        token = await OAuthRefreshToken.objects.filter(
            token_hash=cls.hash_secret(raw_token), revoked=False, expires_at__gt=timezone.now(),
        ).select_related('client', 'user').afirst()
        if token is None:
            return None
        claimed = await OAuthRefreshToken.objects.filter(id=token.id, revoked=False).aupdate(revoked=True)
        return token if claimed else None

    @classmethod
    async def resolve_access_token(cls, raw_token: str) -> OAuthAccessToken | None:
        token = await OAuthAccessToken.objects.filter(
            token_hash=cls.hash_secret(raw_token), revoked=False, expires_at__gt=timezone.now(),
        ).select_related('user', 'client').afirst()
        if token is None:
            return None
        now = timezone.now()
        stale_before = now - timedelta(seconds=ACCESS_TOKEN_LAST_USED_RESOLUTION_SECONDS)
        if token.last_used_at is None or token.last_used_at < stale_before:
            token.last_used_at = now
            await token.asave(update_fields=['last_used_at'])
        return token

    @classmethod
    async def revoke_token(cls, raw_token: str) -> None:
        token_hash = cls.hash_secret(raw_token)
        await OAuthAccessToken.objects.filter(token_hash=token_hash).aupdate(revoked=True)
        await OAuthRefreshToken.objects.filter(token_hash=token_hash).aupdate(revoked=True)

    @classmethod
    async def get_client_for_redirect(cls, client_id: str, redirect_uri: str) -> OAuthClient:
        client = await OAuthClient.objects.filter(client_id=client_id).afirst()
        if client is None or redirect_uri not in client.redirect_uris:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Unknown client or redirect URI.',
                error_code='invalid_oauth_client',
            )
        return client

    @classmethod
    async def get_client_info(cls, client_id: str, redirect_uri: str) -> OAuthClientInfo:
        client = await cls.get_client_for_redirect(client_id, redirect_uri)
        return OAuthClientInfo(
            client_name=client.client_name,
            redirect_host=urlparse(redirect_uri).hostname or '',
        )

    @classmethod
    async def approve(cls, user: User, request: OAuthConsentRequest) -> str:
        """Record the user's consent decision and return the URL that hands control back to Claude:
        an authorization code on approval, or an access_denied error otherwise."""
        client = await cls.get_client_for_redirect(request.client_id, request.redirect_uri)
        if not request.approve:
            return _redirect_url(request.redirect_uri, {'error': 'access_denied', 'state': request.state})
        if not request.code_challenge or request.code_challenge_method != PKCE_METHOD_S256:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='PKCE with code_challenge_method=S256 is required.',
                error_code='pkce_required',
            )
        raw_code = await cls.create_authorization_code(
            client=client,
            user=user,
            redirect_uri=request.redirect_uri,
            scope=MCP_SCOPE,
            resource=request.resource,
            code_challenge=request.code_challenge,
            code_challenge_method=request.code_challenge_method,
        )
        return _redirect_url(request.redirect_uri, {'code': raw_code, 'state': request.state})


def _redirect_url(redirect_uri: str, params: dict[str, str]) -> str:
    separator = '&' if '?' in redirect_uri else '?'
    return f'{redirect_uri}{separator}{urlencode(params)}'

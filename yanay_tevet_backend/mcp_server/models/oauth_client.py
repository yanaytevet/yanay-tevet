from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django.db.models import Manager
    from mcp_server.models.oauth_authorization_code import OAuthAuthorizationCode
    from mcp_server.models.oauth_access_token import OAuthAccessToken
    from mcp_server.models.oauth_refresh_token import OAuthRefreshToken


class OAuthClient(models.Model):
    """An OAuth 2.1 client, typically registered dynamically (RFC 7591) by Claude."""

    if TYPE_CHECKING:
        id: int
        authorization_codes: 'Manager[OAuthAuthorizationCode]'
        access_tokens: 'Manager[OAuthAccessToken]'
        refresh_tokens: 'Manager[OAuthRefreshToken]'

    client_id = models.CharField(max_length=255, unique=True)
    # Empty for public clients (token_endpoint_auth_method == 'none'), which authenticate via PKCE.
    client_secret = models.CharField(max_length=255, blank=True, default='')
    client_name = models.CharField(max_length=255, blank=True, default='')
    redirect_uris: list[str] = models.JSONField(default=list)
    grant_types: list[str] = models.JSONField(default=list)
    response_types: list[str] = models.JSONField(default=list)
    token_endpoint_auth_method = models.CharField(max_length=64, default='none')
    scope = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'OAuthClient({self.client_id}) - {self.client_name}'

    def is_public(self) -> bool:
        return self.token_endpoint_auth_method == 'none' or not self.client_secret

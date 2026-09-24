from mcp.server.auth.provider import AccessToken, TokenVerifier

from mcp_server.config import MCP_SCOPE
from mcp_server.managers.oauth_manager import OAuthManager


class DjangoTokenVerifier(TokenVerifier):
    """Verifies MCP bearer tokens against the OAuthAccessToken table.

    The resolved user id is carried in `AccessToken.subject`; tools read it back via
    `mcp_server.mcp.context.get_current_user`.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        record = await OAuthManager.resolve_access_token(token)
        if record is None:
            return None
        return AccessToken(
            token=token,
            client_id=record.client.client_id,
            scopes=record.scope.split() if record.scope else [MCP_SCOPE],
            expires_at=int(record.expires_at.timestamp()),
            subject=str(record.user_id),
        )

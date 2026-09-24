from mcp.server.auth.middleware.auth_context import get_access_token

from users.models import User


class McpAuthError(Exception):
    """Raised when the current MCP request has no valid authenticated user."""


async def get_current_user() -> User:
    """Return the authenticated user for the in-flight MCP tool call.

    The user id was placed in the access token's `subject` by DjangoTokenVerifier.
    """
    access_token = get_access_token()
    if access_token is None or not access_token.subject:
        raise McpAuthError('No authenticated user in the current request context.')
    user = await User.objects.filter(id=int(access_token.subject)).afirst()
    if user is None:
        raise McpAuthError('Authenticated user no longer exists.')
    return user

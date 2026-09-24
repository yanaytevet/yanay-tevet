from django.http import HttpRequest, JsonResponse

from mcp_server.config import MCP_SCOPE, get_public_base_url, mcp_resource_url


async def authorization_server_metadata(request: HttpRequest) -> JsonResponse:
    """RFC 8414 authorization server metadata, discovered by Claude via the
    protected-resource metadata that the MCP resource server advertises."""
    base = get_public_base_url()
    return JsonResponse({
        'issuer': base,
        'authorization_endpoint': f'{base}/oauth/authorize',
        'token_endpoint': f'{base}/oauth/token',
        'registration_endpoint': f'{base}/oauth/register',
        'revocation_endpoint': f'{base}/oauth/revoke',
        'scopes_supported': [MCP_SCOPE],
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code', 'refresh_token'],
        'code_challenge_methods_supported': ['S256'],
        'token_endpoint_auth_methods_supported': ['none', 'client_secret_post'],
    })


async def protected_resource_metadata(request: HttpRequest) -> JsonResponse:
    """RFC 9728 protected-resource metadata. The MCP app also serves this, but we
    expose it at the well-known root as a convenience/fallback."""
    return JsonResponse({
        'resource': mcp_resource_url(),
        'authorization_servers': [get_public_base_url()],
        'scopes_supported': [MCP_SCOPE],
        'bearer_methods_supported': ['header'],
    })

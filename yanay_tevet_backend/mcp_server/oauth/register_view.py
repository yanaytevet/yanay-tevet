import json
import secrets
import time

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mcp_server.config import is_allowed_redirect_uri
from mcp_server.managers.oauth_manager import OAuthManager
from mcp_server.models.oauth_client import OAuthClient

_MAX_CLIENT_NAME_LENGTH = 255


def _error(message: str, error: str = 'invalid_client_metadata', status: int = 400) -> JsonResponse:
    return JsonResponse({'error': error, 'error_description': message}, status=status)


@csrf_exempt
async def register_client(request: HttpRequest) -> JsonResponse:
    """RFC 7591 Dynamic Client Registration endpoint."""
    if request.method != 'POST':
        return _error('Method not allowed', status=405)
    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return _error('Body must be valid JSON')
    if not isinstance(body, dict):
        return _error('Body must be a JSON object')

    redirect_uris = body.get('redirect_uris')
    if not isinstance(redirect_uris, list) or not redirect_uris:
        return _error('redirect_uris is required and must be a non-empty array')
    if not all(isinstance(uri, str) for uri in redirect_uris):
        return _error('redirect_uris must be an array of strings')
    if not all(is_allowed_redirect_uri(uri) for uri in redirect_uris):
        return _error('This server only accepts Claude or loopback redirect URIs.', error='invalid_redirect_uri')

    grant_types = body.get('grant_types') or ['authorization_code', 'refresh_token']
    response_types = body.get('response_types') or ['code']
    token_endpoint_auth_method = body.get('token_endpoint_auth_method') or 'none'
    client_name = str(body.get('client_name') or '')[:_MAX_CLIENT_NAME_LENGTH]
    scope = str(body.get('scope') or '')

    client_id = f'mcp-{secrets.token_urlsafe(16)}'
    client_secret = ''
    if token_endpoint_auth_method != 'none':
        client_secret = OAuthManager.generate_secret()

    await OAuthClient.objects.acreate(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name,
        redirect_uris=redirect_uris,
        grant_types=grant_types,
        response_types=response_types,
        token_endpoint_auth_method=token_endpoint_auth_method,
        scope=scope,
    )

    response = {
        'client_id': client_id,
        'client_id_issued_at': int(time.time()),
        'redirect_uris': redirect_uris,
        'grant_types': grant_types,
        'response_types': response_types,
        'token_endpoint_auth_method': token_endpoint_auth_method,
        'client_name': client_name,
        'scope': scope,
    }
    if client_secret:
        response['client_secret'] = client_secret
        response['client_secret_expires_at'] = 0  # never expires

    return JsonResponse(response, status=201)

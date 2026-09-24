import secrets

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mcp_server.config import ACCESS_TOKEN_TTL_SECONDS, MCP_SCOPE
from mcp_server.managers.oauth_manager import OAuthManager
from mcp_server.models.oauth_client import OAuthClient
from users.models import User


def _error(error: str, description: str = '', status: int = 400) -> JsonResponse:
    payload = {'error': error}
    if description:
        payload['error_description'] = description
    return JsonResponse(payload, status=status)


async def _authenticate_client(request: HttpRequest, client_id: str) -> OAuthClient | None:
    client = await OAuthClient.objects.filter(client_id=client_id).afirst()
    if client is None:
        return None
    if client.is_public():
        return client
    provided_secret = request.POST.get('client_secret', '')
    if not provided_secret or not secrets.compare_digest(provided_secret, client.client_secret):
        return None
    return client


async def _token_response(client: OAuthClient, user: User, resource: str) -> JsonResponse:
    # There is a single scope; it is always granted as-is rather than echoing what the client asked for.
    access_token, _ = await OAuthManager.create_access_token(client, user, MCP_SCOPE, resource)
    refresh_token = await OAuthManager.create_refresh_token(client, user, MCP_SCOPE, resource)
    return JsonResponse({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_TTL_SECONDS,
        'refresh_token': refresh_token,
        'scope': MCP_SCOPE,
    })


@csrf_exempt
async def token(request: HttpRequest) -> JsonResponse:
    """OAuth 2.1 token endpoint (authorization_code and refresh_token grants)."""
    if request.method != 'POST':
        return _error('invalid_request', 'Method not allowed', status=405)

    grant_type = request.POST.get('grant_type', '')
    client_id = request.POST.get('client_id', '')

    client = await _authenticate_client(request, client_id)
    if client is None:
        return _error('invalid_client', 'Unknown client or bad client authentication', status=401)

    if grant_type == 'authorization_code':
        return await _handle_authorization_code(request, client)
    if grant_type == 'refresh_token':
        return await _handle_refresh_token(request, client)
    return _error('unsupported_grant_type', f'Unsupported grant_type: {grant_type}')


async def _handle_authorization_code(request: HttpRequest, client: OAuthClient) -> JsonResponse:
    raw_code = request.POST.get('code', '')
    redirect_uri = request.POST.get('redirect_uri', '')
    code_verifier = request.POST.get('code_verifier', '')

    code = await OAuthManager.consume_authorization_code(raw_code)
    if code is None or code.client_id != client.id:
        return _error('invalid_grant', 'Authorization code is invalid or expired')
    if code.redirect_uri != redirect_uri:
        return _error('invalid_grant', 'redirect_uri does not match the authorization request')
    if not OAuthManager.verify_pkce(code_verifier, code.code_challenge, code.code_challenge_method):
        return _error('invalid_grant', 'PKCE verification failed')

    return await _token_response(client, code.user, code.resource)


async def _handle_refresh_token(request: HttpRequest, client: OAuthClient) -> JsonResponse:
    raw_refresh = request.POST.get('refresh_token', '')
    token_record = await OAuthManager.consume_refresh_token(raw_refresh)
    if token_record is None or token_record.client_id != client.id:
        return _error('invalid_grant', 'Refresh token is invalid or expired')
    return await _token_response(client, token_record.user, token_record.resource)

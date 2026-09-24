from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from mcp_server.managers.oauth_manager import PKCE_METHOD_S256
from mcp_server.models.oauth_client import OAuthClient

# OAuth request parameters forwarded to the frontend consent page.
_FORWARDED_PARAMS = (
    'client_id', 'redirect_uri', 'response_type', 'scope', 'state',
    'code_challenge', 'code_challenge_method', 'resource',
)

# Frontend route that renders the login + consent screen.
_CONSENT_PATH = '/connect-claude'


async def _load_valid_client(client_id: str, redirect_uri: str) -> OAuthClient | None:
    client = await OAuthClient.objects.filter(client_id=client_id).afirst()
    if client is None or redirect_uri not in client.redirect_uris:
        return None
    return client


def _error_redirect(redirect_uri: str, error: str, description: str, state: str) -> HttpResponseRedirect:
    separator = '&' if '?' in redirect_uri else '?'
    query = urlencode({'error': error, 'error_description': description, 'state': state})
    return HttpResponseRedirect(f'{redirect_uri}{separator}{query}')


@csrf_exempt
async def authorize(request: HttpRequest) -> HttpResponse:
    """OAuth 2.1 authorization endpoint.

    Authentication and consent happen in the web app (so users get the normal login, including
    Google sign-in and passkeys), not here. After validating the request we redirect the browser to
    the frontend consent page, which finishes the flow via POST /api/mcp/oauth/approve/.
    """
    params = {name: request.GET.get(name, '') for name in _FORWARDED_PARAMS}
    client = await _load_valid_client(params['client_id'], params['redirect_uri'])
    if client is None:
        # Never redirect to an unvalidated URI; show an inline error instead.
        return HttpResponse('Invalid client_id or redirect_uri.', status=400)

    if params['response_type'] != 'code':
        return _error_redirect(params['redirect_uri'], 'unsupported_response_type',
                               'response_type must be "code".', params['state'])
    if not params['code_challenge'] or params['code_challenge_method'] != PKCE_METHOD_S256:
        return _error_redirect(params['redirect_uri'], 'invalid_request',
                               'PKCE with code_challenge_method=S256 is required.', params['state'])

    consent_url = (
        f'{settings.FRONTEND_URL.rstrip("/")}{_CONSENT_PATH}?'
        f'{urlencode({k: v for k, v in params.items() if v})}'
    )
    return HttpResponseRedirect(consent_url)

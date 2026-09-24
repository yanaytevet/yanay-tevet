from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from mcp_server.managers.oauth_manager import OAuthManager


@csrf_exempt
async def revoke(request: HttpRequest) -> HttpResponse:
    """RFC 7009 token revocation. Always returns 200, per spec, even for unknown tokens."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    raw_token = request.POST.get('token', '')
    if raw_token:
        await OAuthManager.revoke_token(raw_token)
    return HttpResponse(status=200)

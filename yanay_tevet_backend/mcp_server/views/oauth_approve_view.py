from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from mcp_server.managers.oauth_manager import OAuthManager
from mcp_server.schemas.oauth_consent_schemas import OAuthConsentRequest, OAuthConsentResult


class OAuthApproveView(SimplePostAPIView):
    """Completes the OAuth flow after the user has logged in and consented in the web app.

    Called by the frontend consent page with the user's normal app credentials (JWT), so the
    authorization code is bound to the logged-in user.
    """

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return OAuthConsentRequest

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return OAuthConsentResult

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, data: Schema, path: Path = None) -> None:
        user = await api_request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, api_request: APIRequest, data: OAuthConsentRequest, path: Path = None
                         ) -> OAuthConsentResult:
        user = await api_request.future_user
        redirect_url = await OAuthManager.approve(user, data)
        return OAuthConsentResult(redirect_url=redirect_url)

from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from mcp_server.managers.oauth_manager import OAuthManager
from mcp_server.schemas.oauth_consent_schemas import OAuthClientInfo, OAuthClientInfoQuery


class GetOAuthClientInfoView(SimpleGetAPIView):
    """Describes the OAuth client asking for access, for the consent screen."""

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return OAuthClientInfo

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return OAuthClientInfoQuery

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        user = await api_request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: OAuthClientInfoQuery = None, path: Path = None
                       ) -> OAuthClientInfo:
        return await OAuthManager.get_client_info(query.client_id, query.redirect_uri)

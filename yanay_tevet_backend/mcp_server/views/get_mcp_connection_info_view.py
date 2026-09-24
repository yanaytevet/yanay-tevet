from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from mcp_server.managers.mcp_connection_manager import McpConnectionManager
from mcp_server.schemas.oauth_consent_schemas import McpConnectionInfo


class GetMcpConnectionInfoView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return McpConnectionInfo

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        user = await api_request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> McpConnectionInfo:
        return McpConnectionManager().get_connection_info()

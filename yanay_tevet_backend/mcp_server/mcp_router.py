from common.django_utils.api_router_creator import ApiRouterCreator
from mcp_server.views.get_mcp_connection_info_view import GetMcpConnectionInfoView
from mcp_server.views.get_oauth_client_info_view import GetOAuthClientInfoView
from mcp_server.views.oauth_approve_view import OAuthApproveView

api, router = ApiRouterCreator.create_api_and_router('mcp')

GetMcpConnectionInfoView.register_get(router, 'connection-info/')
GetOAuthClientInfoView.register_get(router, 'oauth/client-info/')
OAuthApproveView.register_post(router, 'oauth/approve/')

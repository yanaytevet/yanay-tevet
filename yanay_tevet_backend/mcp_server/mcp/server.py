from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from mcp_server.config import MCP_PATH, MCP_SCOPE, get_public_base_url, mcp_resource_url
from mcp_server.mcp.token_verifier import DjangoTokenVerifier
from mcp_server.mcp.tools import shopping_list_tools, task_tools

INSTRUCTIONS = (
    "Tools for the user's personal Yanay Tevet workspace. "
    'Tasks: work is grouped into projects — call list_task_projects to find a project id, '
    'get_task_project to see its tasks, then create_tasks / update_task / delete_task / reorder_tasks. '
    'Shopping lists: call list_shopping_lists to find a list id, get_shopping_list to see its items, '
    'then add_shopping_items / update_shopping_items / delete_shopping_items. '
    'All changes show up in the web app immediately and are visible to everyone the project or list '
    'is shared with.'
)


def build_mcp_server() -> FastMCP:
    """Build the FastMCP resource server: verifies bearer tokens against our OAuth
    authorization server and exposes the app's tools."""
    mcp = FastMCP(
        name='Yanay Tevet',
        instructions=INSTRUCTIONS,
        token_verifier=DjangoTokenVerifier(),
        auth=AuthSettings(
            issuer_url=get_public_base_url(),
            resource_server_url=mcp_resource_url(),
            required_scopes=[MCP_SCOPE],
        ),
        streamable_http_path=MCP_PATH,
        # Stateless: every request stands alone, so dev autoreloads and prod restarts don't strand
        # Claude on a session id the process no longer knows. No tool needs server-held session state.
        stateless_http=True,
        # DNS-rebinding protection guards browser-reachable localhost servers by pinning the Host
        # header. This is a remote server reached through a tunnel/reverse proxy (so the Host is the
        # public domain, not localhost) and every request is OAuth-authenticated, so that protection
        # doesn't apply and would only reject the legitimate public Host.
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    task_tools.register(mcp)
    shopping_list_tools.register(mcp)
    return mcp

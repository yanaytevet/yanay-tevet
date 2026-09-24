from urllib.parse import urlencode

from mcp_server.config import mcp_resource_url
from mcp_server.schemas.oauth_consent_schemas import McpConnectionInfo

CONNECTOR_NAME = 'Yanay Tevet'


class McpConnectionManager:
    def get_connection_info(self) -> McpConnectionInfo:
        mcp_url = mcp_resource_url()
        add_connector_url = 'https://claude.ai/settings/connectors?' + urlencode({
            'modal': 'add-custom-connector',
            'mcpName': CONNECTOR_NAME,
            'mcpServerUrl': mcp_url,
        })
        return McpConnectionInfo(
            mcp_url=mcp_url,
            add_connector_url=add_connector_url,
            is_publicly_reachable=mcp_url.startswith('https://'),
        )

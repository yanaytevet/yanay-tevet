from ninja import Schema


class OAuthConsentRequest(Schema):
    client_id: str
    redirect_uri: str
    scope: str = ''
    state: str = ''
    code_challenge: str = ''
    code_challenge_method: str = ''
    resource: str = ''
    approve: bool


class OAuthConsentResult(Schema):
    # Where the browser should navigate to hand control back to Claude.
    redirect_url: str


class OAuthClientInfoQuery(Schema):
    client_id: str
    redirect_uri: str


class OAuthClientInfo(Schema):
    # Name the client registered itself with (e.g. "Claude") — shown on the consent screen.
    client_name: str
    # Host the authorization code will be sent to, so the user can see where they are granting access.
    redirect_host: str


class McpConnectionInfo(Schema):
    # The remote MCP server URL to paste into Claude as a custom connector.
    mcp_url: str
    # Deep link that opens Claude's "Add custom connector" dialog pre-filled with the URL.
    add_connector_url: str
    # False when the URL is a bare localhost (no public tunnel) — Claude can't reach it.
    is_publicly_reachable: bool

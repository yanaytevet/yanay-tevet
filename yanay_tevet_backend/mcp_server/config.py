import functools
import json
import os
import urllib.request
from urllib.parse import urlparse

from django.conf import settings

# The MCP streamable-HTTP endpoint path (mounted inside the Django ASGI app).
MCP_PATH: str = '/mcp'

# Single OAuth scope that grants access to the MCP tools. Kept intentionally coarse for now;
# finer-grained scopes can be added later without breaking existing connectors.
MCP_SCOPE: str = 'yanay-tevet'

# Lifetimes.
AUTHORIZATION_CODE_TTL_SECONDS: int = 5 * 60
ACCESS_TOKEN_TTL_SECONDS: int = 60 * 60
REFRESH_TOKEN_TTL_SECONDS: int = 30 * 24 * 60 * 60

# How stale `OAuthAccessToken.last_used_at` may get before a request refreshes it. Avoids a DB
# write on every single MCP call.
ACCESS_TOKEN_LAST_USED_RESOLUTION_SECONDS: int = 5 * 60

# Dynamic client registration is open to anyone, so the redirect URIs a client may register are
# restricted. Otherwise anyone could register a client pointing at their own server and phish a
# logged-in user through the consent page into handing over an authorization code.
# Allowed: Claude's hosted callbacks (claude.ai / Claude Desktop) and loopback (Claude Code, MCP
# Inspector), which only reaches the user's own machine.
ALLOWED_REDIRECT_HOSTS: frozenset[str] = frozenset({'claude.ai', 'claude.com'})
LOOPBACK_REDIRECT_HOSTS: frozenset[str] = frozenset({'localhost', '127.0.0.1'})

# ngrok's agent exposes a local API listing active tunnels. The backend runs inside Docker,
# so the host's ngrok agent (bound to the host loopback) is reached via host.docker.internal
# on Docker Desktop; the plain loopback hosts cover running the backend outside a container.
_NGROK_API_HOSTS: tuple[str, ...] = ('host.docker.internal', 'localhost', '127.0.0.1')
_NGROK_API_PORT: int = 4040


def is_allowed_redirect_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    if parsed.scheme == 'https' and parsed.hostname in ALLOWED_REDIRECT_HOSTS:
        return True
    return parsed.scheme == 'http' and parsed.hostname in LOOPBACK_REDIRECT_HOSTS


def _discover_ngrok_base_url() -> str | None:
    for host in _NGROK_API_HOSTS:
        try:
            with urllib.request.urlopen(f'http://{host}:{_NGROK_API_PORT}/api/tunnels', timeout=0.5) as resp:
                tunnels = json.loads(resp.read()).get('tunnels', [])
        except (OSError, ValueError):
            continue
        for tunnel in tunnels:
            public_url = tunnel.get('public_url', '')
            if public_url.startswith('https://'):
                return public_url.rstrip('/')
    return None


@functools.lru_cache(maxsize=1)
def get_public_base_url() -> str:
    """Public, externally reachable base URL of THIS backend that Claude connects to (no trailing
    slash) — the MCP server lives on the backend, so this is the backend's own public origin, NOT
    the frontend's.

    Resolution:
    1. ``MCP_PUBLIC_BASE_URL`` env — set this in production, e.g. ``https://api.yanaytevet.com``.
    2. In dev (``DEBUG``) with it unset, auto-discover the current ngrok tunnel from the ngrok
       agent's local API, so restarting ngrok "just works" without editing any config.
    3. ``http://localhost:8000`` as a last resort.

    Claude uses this to discover the OAuth authorization server and the MCP resource, so it MUST
    match the host Claude connects to. Cached for the process lifetime; restart the backend after
    changing it (or after starting/restarting ngrok).
    """
    explicit = os.environ.get('MCP_PUBLIC_BASE_URL', '').rstrip('/')
    if explicit:
        return explicit
    if settings.DEBUG:
        discovered = _discover_ngrok_base_url()
        if discovered:
            return discovered
    return 'http://localhost:8000'


def mcp_resource_url() -> str:
    return f'{get_public_base_url()}{MCP_PATH}'

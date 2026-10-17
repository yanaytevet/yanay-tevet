'''
ASGI config for yanay_tevet_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
'''

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.conf import settings
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yanay_tevet_backend.settings')

django_asgi_app = get_asgi_application()
django.setup()


import yanay_tevet_backend.routing
from mcp_server.config import MCP_PATH
from mcp_server.mcp.asgi_app import mcp_asgi_app


def _is_mcp_path(path: str) -> bool:
    """MCP owns its streamable endpoint plus the resource-scoped OAuth metadata document."""
    return (
        path == MCP_PATH
        or path.startswith(f'{MCP_PATH}/')
        or path == f'/.well-known/oauth-protected-resource{MCP_PATH}'
    )


async def http_router(scope, receive, send) -> None:
    if _is_mcp_path(scope['path']):
        await mcp_asgi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)


async def lifespan_app(scope, receive, send) -> None:
    """Minimal ASGI lifespan handler so servers that emit lifespan (uvicorn in production) don't
    error. The MCP session manager is started lazily in mcp_server.mcp.asgi_app."""
    while True:
        message = await receive()
        if message['type'] == 'lifespan.startup':
            await send({'type': 'lifespan.startup.complete'})
        elif message['type'] == 'lifespan.shutdown':
            await send({'type': 'lifespan.shutdown.complete'})
            return


application = ProtocolTypeRouter(
    {
        'http': http_router,
        # A websocket is opened by the frontend, so its Origin is the frontend's address, checked against
        # the origins CORS already trusts. AllowedHostsOriginValidator would check it against
        # ALLOWED_HOSTS, the backend's own hostnames, and refuse every socket in production, where
        # yanaytevet.com and api.yanaytevet.com differ.
        'websocket': OriginValidator(
            AuthMiddlewareStack(URLRouter(yanay_tevet_backend.routing.websocket_urlpatterns)),
            settings.ALLOWED_ORIGINS,
        ),
        'lifespan': lifespan_app,
    }
)

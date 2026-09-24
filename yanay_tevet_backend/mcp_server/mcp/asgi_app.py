import asyncio

from mcp_server.mcp.server import build_mcp_server

# Built once at import time (after django.setup()). The streamable_http_app() call also
# creates the session manager, which we must access afterwards.
_mcp = build_mcp_server()
_starlette_app = _mcp.streamable_http_app()
_session_manager = _mcp.session_manager

_ready = asyncio.Event()
_started = False


async def _run_session_manager() -> None:
    """Hold the StreamableHTTP session manager's run() context open for the whole process.

    The dev server (Daphne, via `manage.py runserver`) does not emit the ASGI lifespan
    protocol, so we cannot rely on the Starlette app's own lifespan to start the session
    manager. We start it lazily in a long-lived background task instead — one that works
    identically under Daphne and uvicorn.
    """
    async with _session_manager.run():
        _ready.set()
        await asyncio.Event().wait()  # never set; keeps the run() context alive


async def mcp_asgi_app(scope, receive, send) -> None:
    global _started
    if scope['type'] == 'lifespan':
        # Lifespan is owned by the top-level ASGI router; never drive the Starlette
        # app's lifespan here or the session manager would be started twice.
        return
    if not _started:
        # Safe without a lock: assignment happens before any await, and asyncio is
        # cooperative, so concurrent first requests cannot both pass this check.
        _started = True
        asyncio.ensure_future(_run_session_manager())
    await _ready.wait()
    await _starlette_app(scope, receive, send)

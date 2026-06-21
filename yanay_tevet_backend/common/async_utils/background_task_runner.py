import asyncio
import contextvars
import logging
import threading
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# Keep strong references to the runner threads so they are not garbage collected
# while still doing work.
_background_threads: set[threading.Thread] = set()

# The server's main event loop, captured from the request that spawned the task.
#
# The background task runs on its own throwaway loop (see _run), but channel-layer
# broadcasts (group_send) must run on the main server loop — that loop owns the
# websocket consumers and their Redis receive connections. Publishing from the
# throwaway loop uses connections bound to a loop that is about to be torn down,
# which silently dropped the "generation finished" message in production (uvicorn
# uses uvloop, the dev server uses plain asyncio — hence the prod-only symptom).
#
# BaseWebsocketEventsManager reads this to redirect its group_send onto the main
# loop via run_coroutine_threadsafe. Outside a background task it stays None and
# the broadcast runs inline on whatever loop is already current.
server_event_loop: contextvars.ContextVar[asyncio.AbstractEventLoop | None] = contextvars.ContextVar(
    'server_event_loop', default=None,
)


def run_in_background(coro: Coroutine[Any, Any, Any]) -> None:
    """Run a coroutine fully detached from the current request.

    We deliberately do NOT use asyncio.create_task here. That would schedule the
    coroutine on the request's event loop, where Django's thread-sensitive
    sync_to_async (used by all ORM access and serialization) is bound to the
    request's CurrentThreadExecutor. As soon as the HTTP response is sent that
    executor is torn down, and any further ORM/serialization work in the task
    fails with "CurrentThreadExecutor already quit or is broken" — which silently
    dropped the websocket broadcast at the end of content generation.

    Running the coroutine in its own thread + event loop gives it a fresh executor
    that lives for the entire task, independent of the request lifecycle.

    We capture the caller's (server's main) event loop and hand it to the task so
    that channel-layer broadcasts can be run back on it — see server_event_loop.
    """
    try:
        main_loop = asyncio.get_running_loop()
    except RuntimeError:
        main_loop = None
    thread = threading.Thread(target=_run, args=(coro, main_loop), daemon=True)
    _background_threads.add(thread)
    thread.start()


def _run(coro: Coroutine[Any, Any, Any], main_loop: asyncio.AbstractEventLoop | None) -> None:
    # Set before asyncio.run so the value is captured into the task's context and
    # is visible to every coroutine it awaits.
    server_event_loop.set(main_loop)
    try:
        asyncio.run(coro)
    except Exception:
        logger.error('Background task failed', exc_info=True)
    finally:
        _background_threads.discard(threading.current_thread())

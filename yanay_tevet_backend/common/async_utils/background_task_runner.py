import asyncio
import logging
import threading
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# Keep strong references to the runner threads so they are not garbage collected
# while still doing work.
_background_threads: set[threading.Thread] = set()


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
    """
    thread = threading.Thread(target=_run, args=(coro,), daemon=True)
    _background_threads.add(thread)
    thread.start()


def _run(coro: Coroutine[Any, Any, Any]) -> None:
    try:
        asyncio.run(coro)
    except Exception:
        logger.error('Background task failed', exc_info=True)
    finally:
        _background_threads.discard(threading.current_thread())

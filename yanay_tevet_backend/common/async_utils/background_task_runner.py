import asyncio
import logging
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# asyncio only keeps weak references to tasks, so a fire-and-forget task can be
# garbage collected before it finishes. Keep a strong reference until it's done.
_background_tasks: set[asyncio.Task] = set()


def run_in_background(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_on_task_done)
    return task


def _on_task_done(task: asyncio.Task) -> None:
    _background_tasks.discard(task)
    if task.cancelled():
        return
    exception = task.exception()
    if exception is not None:
        logger.error('Background task failed', exc_info=exception)

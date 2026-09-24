import functools
from collections.abc import Awaitable, Callable
from typing import TypeVar

from common.simple_api.exceptions.rest_api_exception import RestAPIException
from mcp_server.mcp.context import McpAuthError

T = TypeVar('T')


def handle_tool_errors(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Translate internal exceptions into clean, user-facing tool errors.

    Permission, not-found and validation failures raised by the web API's checkers and managers
    become ValueErrors whose message the MCP client shows verbatim, instead of leaking framework
    exception reprs.
    """

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await fn(*args, **kwargs)
        except RestAPIException as exc:
            raise ValueError(exc.message) from exc
        except McpAuthError as exc:
            raise ValueError(str(exc)) from exc

    return wrapper

import asyncio
from abc import ABC, abstractmethod
from typing import Self

from channels.layers import get_channel_layer

from common.async_utils.background_task_runner import server_event_loop
from common.type_hints import JSONType
from users.models import User


class BaseWebsocketEventsManager(ABC):

    async def async_send_event_to_group(self, data: JSONType) -> None:
        group_name = self.get_group_name()
        message = {
            'data': {
                'group_name': group_name,
                'event_type': self.get_event_type(),
                'payload': data
            },
            'type': 'send_event_to_user',
        }
        channel_layer = get_channel_layer()
        main_loop = server_event_loop.get()
        running_loop = asyncio.get_running_loop()
        if main_loop is not None and main_loop is not running_loop:
            # We're on a detached background loop (see run_in_background). The
            # channel layer's connections and the websocket consumers live on the
            # main server loop, so publish there instead — otherwise the message
            # goes out on a connection bound to this throwaway loop and is dropped.
            future = asyncio.run_coroutine_threadsafe(
                channel_layer.group_send(group_name, message), main_loop,
            )
            await asyncio.wrap_future(future)
        else:
            await channel_layer.group_send(group_name, message)

    @abstractmethod
    def get_group_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_event_type(cls) -> str:
        raise NotImplementedError()

    async def subscribe(self, channel_name: str, user: User) -> bool:
        await self.check_permitted(user)
        channel_layer = get_channel_layer()
        await channel_layer.group_add(self.get_group_name(), channel_name)
        return True

    @abstractmethod
    async def check_permitted(self, user: User) -> bool:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def generate_from_additional_info(cls, additional_info: JSONType) -> Self:
        raise NotImplementedError()

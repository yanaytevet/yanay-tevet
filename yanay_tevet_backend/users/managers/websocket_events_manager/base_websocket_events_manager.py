from abc import ABC, abstractmethod
from typing import Self

from channels.layers import get_channel_layer

from common.type_hints import JSONType
from users.models import User


class BaseWebsocketEventsManager(ABC):

    async def async_send_event_to_group(self, data: JSONType) -> None:
        group_name = self.get_group_name()
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            group_name,
            {
                'data': {
                    'group_name': group_name,
                    'event_type': self.get_event_type(),
                    'payload': data
                },
                'type': 'send_event_to_user',
            }
        )

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

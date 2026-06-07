from typing import Self

from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.type_hints import JSONType
from users.managers.websocket_events_manager.base_websocket_events_manager import BaseWebsocketEventsManager
from users.models import User


class NodeWebsocketEventManager(BaseWebsocketEventsManager):
    def __init__(self, node_id: int):
        self.node_id = node_id

    def get_group_name(self) -> str:
        return f'japanese_node_{self.node_id}'

    @classmethod
    def get_event_type(cls) -> str:
        return 'japanese_node'

    @classmethod
    def generate_from_additional_info(cls, additional_info: JSONType) -> Self:
        return cls(additional_info['node_id'])

    async def check_permitted(self, user: User) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

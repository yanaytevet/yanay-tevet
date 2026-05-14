from common.type_hints import JSONType
from users.managers.websocket_events_manager.base_websocket_events_manager import BaseWebsocketEventsManager
from users.managers.websocket_events_manager.notifications_websocket_events_manager import \
    NotificationsWebsocketEventManager
from users.managers.websocket_events_manager.room_websocket_events_manager import RoomWebsocketEventManager


class WebsocketEventsManagerGenerator:
    EVENT_TYPE_TO_CLS = {
        RoomWebsocketEventManager.get_event_type(): RoomWebsocketEventManager,
        NotificationsWebsocketEventManager.get_event_type(): NotificationsWebsocketEventManager,
    }

    @classmethod
    def generate(cls, event_type: str, additional_info: JSONType) -> BaseWebsocketEventsManager:
        return cls.EVENT_TYPE_TO_CLS[event_type].generate_from_additional_info(additional_info)

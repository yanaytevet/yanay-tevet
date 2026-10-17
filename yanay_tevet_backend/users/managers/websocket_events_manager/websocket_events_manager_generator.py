from common.type_hints import JSONType
from users.managers.websocket_events_manager.base_websocket_events_manager import BaseWebsocketEventsManager
from users.managers.websocket_events_manager.node_websocket_events_manager import NodeWebsocketEventManager
from users.managers.websocket_events_manager.notifications_websocket_events_manager import \
    NotificationsWebsocketEventManager


class WebsocketEventsManagerGenerator:
    EVENT_TYPE_TO_CLS = {
        NotificationsWebsocketEventManager.get_event_type(): NotificationsWebsocketEventManager,
        NodeWebsocketEventManager.get_event_type(): NodeWebsocketEventManager,
    }

    @classmethod
    def generate(cls, event_type: str, additional_info: JSONType) -> BaseWebsocketEventsManager | None:
        # Both arguments come off a websocket frame, so an unknown event type or an additional_info
        # missing the key a manager reads is ordinary client input: None, not an exception.
        manager_cls = cls.EVENT_TYPE_TO_CLS.get(event_type)
        if manager_cls is None:
            return None
        if not isinstance(additional_info, dict):
            return None
        try:
            return manager_cls.generate_from_additional_info(additional_info)
        except KeyError:
            return None

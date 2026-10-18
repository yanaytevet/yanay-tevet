import json

from channels.generic.websocket import AsyncWebsocketConsumer

from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.managers.django_auth import DjangoAuth
from users.managers.websocket_events_manager.websocket_events_manager_generator import WebsocketEventsManagerGenerator
from yanay_tevet_backend.logger import app_logger


class MainWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        # Every field of a frame is untrusted input, and the socket is shared by every subscription
        # on the page. A frame that makes no sense is logged and ignored rather than raised, which
        # would close the socket for all of them.
        try:
            data = json.loads(text_data or '')
        except (json.JSONDecodeError, TypeError):
            app_logger.logger.info('Websocket frame was not valid JSON; ignoring it.')
            return

        if not isinstance(data, dict) or data.get('action') != 'subscribe':
            return

        event_type = data.get('event_type')
        access_token = data.get('access_token')
        if not event_type or not access_token:
            app_logger.logger.info('Websocket subscribe frame was missing its event type or token.')
            return

        user_obj = await DjangoAuth.get_user_from_access_token(access_token)
        if user_obj is None:
            app_logger.logger.info('Websocket subscribe frame carried no usable access token.')
            return

        manager = WebsocketEventsManagerGenerator().generate(event_type, data.get('additional_info'))
        if manager is None:
            app_logger.logger.info('Websocket subscribe frame asked for an unknown event type.')
            return

        try:
            await manager.subscribe(self.channel_name, user_obj)
        except RestAPIException as error:
            app_logger.logger.info('Websocket subscription refused: %s', error.error_code)
            return

        await self.send(text_data=json.dumps({
            'group_name': manager.get_group_name(),
            'is_connection_event': True,
            'event_type': event_type,
            'action_hash': data.get('action_hash'),
        }))

    async def send_event_to_user(self, event) -> None:
        await self.send(text_data=json.dumps(event['data']))

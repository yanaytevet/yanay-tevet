import json

from channels.generic.websocket import AsyncWebsocketConsumer

from users.managers.django_auth import DjangoAuth
from users.managers.websocket_events_manager.websocket_events_manager_generator import WebsocketEventsManagerGenerator


class MainWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass
        # await self.channel_layer.group_discard(
        #     self.channel_name
        # )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['action'] == 'subscribe':
            event_type = data['event_type']
            additional_info = data['additional_info']
            access_token = data['access_token']
            manager = WebsocketEventsManagerGenerator().generate(event_type, additional_info)
            user_obj = await DjangoAuth.get_user_from_access_token(access_token)
            await manager.subscribe(self.channel_name, user_obj)
            await self.send(text_data=json.dumps({
                'group_name': manager.get_group_name(),
                'is_connection_event': True,
                'event_type': data['event_type'],
                'action_hash': data['action_hash'],
            }))

    async def send_event_to_user(self, event) -> None:
        await self.send(text_data=json.dumps(event['data']))

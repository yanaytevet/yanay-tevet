import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from users.managers.django_auth import DjangoAuth
from users.managers.websocket_events_manager.websocket_events_manager_generator import WebsocketEventsManagerGenerator


# Cloudflare (which proxies wss:// in production) closes a WebSocket once ~100s
# pass with no frames in either direction. Long-running work like Japanese content
# generation leaves the socket idle well past that, so the final broadcast lands on
# a connection Cloudflare has already dropped and the client never sees the result.
# A periodic application-level heartbeat keeps the connection alive. We send a real
# data frame on purpose: Cloudflare does not reliably treat protocol-level ping/pong
# control frames as activity for its idle timer.
HEARTBEAT_INTERVAL_SECONDS = 30


class MainWebsocketConsumer(AsyncWebsocketConsumer):
    _heartbeat_task: asyncio.Task | None = None

    async def connect(self):
        await self.accept()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def disconnect(self, close_code):
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def _heartbeat_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
                await self.send(text_data=json.dumps({'is_heartbeat': True}))
        except asyncio.CancelledError:
            pass

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

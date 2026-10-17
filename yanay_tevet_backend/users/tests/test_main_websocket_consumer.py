import json

from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings

from users.consumers.main_websocket_consumer import MainWebsocketConsumer
from users.managers.django_auth import DjangoAuth
from users.models import User


@override_settings(CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}})
class MainWebsocketConsumerTest(TransactionTestCase):
    """One socket carries every subscription on a page, so a frame that makes no sense has to be
    ignored. If it raised, the socket would close under all of them.

    A TransactionTestCase because channels closes the database connection around each frame, which
    would close a TestCase's wrapping transaction with it."""

    async def connect(self) -> tuple[WebsocketCommunicator, User]:
        user = await User.objects.acreate(username='user@example.com', email='user@example.com')
        communicator = WebsocketCommunicator(MainWebsocketConsumer.as_asgi(), '/ws/socket/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator, user

    def subscribe_frame(self, user: User, user_id: int) -> str:
        return json.dumps({
            'action': 'subscribe',
            'action_hash': 'hash',
            'event_type': 'user_notifications',
            'additional_info': {'user_id': user_id},
            'access_token': DjangoAuth.create_access_token(user.id),
        })

    async def assert_socket_still_subscribes(self, communicator: WebsocketCommunicator, user: User) -> None:
        await communicator.send_to(text_data=self.subscribe_frame(user, user.id))
        reply = json.loads(await communicator.receive_from())
        self.assertEqual(reply['group_name'], f'user_notifications_{user.id}')

    async def test_bad_frames_are_ignored_and_the_socket_survives(self) -> None:
        communicator, user = await self.connect()

        for frame in ('not json', '[1, 2]', json.dumps({'action': 'subscribe'}),
                      json.dumps({'action': 'subscribe', 'event_type': 'nonsense', 'access_token': 'bad'})):
            await communicator.send_to(text_data=frame)
            self.assertTrue(await communicator.receive_nothing(timeout=0.2))

        await self.assert_socket_still_subscribes(communicator, user)
        await communicator.disconnect()

    async def test_a_refused_subscription_gets_no_reply_and_the_socket_survives(self) -> None:
        communicator, user = await self.connect()

        await communicator.send_to(text_data=self.subscribe_frame(user, user.id + 1))
        self.assertTrue(await communicator.receive_nothing(timeout=0.2))

        await self.assert_socket_still_subscribes(communicator, user)
        await communicator.disconnect()

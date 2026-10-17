from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import SimpleTestCase, override_settings

from yanay_tevet_backend.asgi import application


@override_settings(CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}})
class WebsocketOriginTest(SimpleTestCase):
    """A websocket is accepted from the frontend's origin and refused from anywhere else.

    The origin a browser sends is the frontend's, never the API's own host, which is why it is checked
    against ALLOWED_ORIGINS rather than ALLOWED_HOSTS. Checking it against the hosts refuses every socket
    in production, where the two differ."""

    async def connect(self, origin: str) -> bool:
        communicator = WebsocketCommunicator(application, '/ws/socket/', headers=[(b'origin', origin.encode())])
        connected, _ = await communicator.connect()
        await communicator.disconnect()
        return connected

    async def test_the_frontend_origin_is_accepted(self) -> None:
        self.assertTrue(await self.connect(settings.FRONTEND_URL))

    async def test_another_origin_is_refused(self) -> None:
        self.assertFalse(await self.connect('https://evil.example.com'))

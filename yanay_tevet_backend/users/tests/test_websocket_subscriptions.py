from django.test import SimpleTestCase

from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.managers.websocket_events_manager.notifications_websocket_events_manager import (
    NotificationsWebsocketEventManager)
from users.managers.websocket_events_manager.websocket_events_manager_generator import (
    WebsocketEventsManagerGenerator)
from users.models import User


class NotificationsSubscriptionScopeTest(SimpleTestCase):
    """The group a subscription joins is named after a user id that came off the frame, so being
    logged in cannot be the whole check — the id has to be the subscriber's own."""

    async def test_a_user_may_subscribe_to_their_own_notifications(self) -> None:
        user = User(id=7, username='seven@example.com')
        await NotificationsWebsocketEventManager(user_id=7).check_permitted(user)

    async def test_a_user_may_not_subscribe_to_another_users_notifications(self) -> None:
        user = User(id=7, username='seven@example.com')
        with self.assertRaises(RestAPIException) as raised:
            await NotificationsWebsocketEventManager(user_id=8).check_permitted(user)
        self.assertEqual(raised.exception.error_code, 'cannot_subscribe_to_other_user_notifications')

    async def test_an_anonymous_subscriber_is_refused(self) -> None:
        with self.assertRaises(RestAPIException) as raised:
            await NotificationsWebsocketEventManager(user_id=8).check_permitted(None)
        self.assertEqual(raised.exception.error_code, 'must_be_logged_in')


class ManagerGeneratorTest(SimpleTestCase):
    """Both arguments come off a websocket frame, so neither may raise out of the generator — an
    exception here kills the connection instead of dropping one bad frame."""

    def test_builds_a_manager_for_a_known_event_type(self) -> None:
        manager = WebsocketEventsManagerGenerator.generate('user_notifications', {'user_id': 7})
        self.assertIsInstance(manager, NotificationsWebsocketEventManager)

    def test_returns_none_for_an_unknown_event_type(self) -> None:
        self.assertIsNone(WebsocketEventsManagerGenerator.generate('nonsense', {'user_id': 7}))

    def test_returns_none_when_additional_info_is_missing_its_key(self) -> None:
        self.assertIsNone(WebsocketEventsManagerGenerator.generate('user_notifications', {}))

    def test_returns_none_when_additional_info_is_not_an_object(self) -> None:
        self.assertIsNone(WebsocketEventsManagerGenerator.generate('user_notifications', 'nope'))
        self.assertIsNone(WebsocketEventsManagerGenerator.generate('user_notifications', None))

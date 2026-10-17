from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.websocket_events_manager.notifications_websocket_events_manager import \
    NotificationsWebsocketEventManager


class PostSampleWebsocketViewSchema(Schema):
    message: str = 'Hello from websocket!'


# Pushes to the caller's own notifications. The group comes from the signed-in user, never from the
# request: a group named after an id the client sent would let a caller push into someone else's stream.
class PostSampleWebsocketView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return PostSampleWebsocketViewSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: PostSampleWebsocketViewSchema, path: Path = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: PostSampleWebsocketViewSchema, path: Path = None) -> EmptySchema:
        user = await request.future_user
        await NotificationsWebsocketEventManager(user_id=user.id).async_send_event_to_group({'message': data.message})
        return EmptySchema()

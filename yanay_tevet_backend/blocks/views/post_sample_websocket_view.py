from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.websocket_events_manager.room_websocket_events_manager import RoomWebsocketEventManager


class PostSampleWebsocketViewSchema(Schema):
    room_id: int


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
        room_id = data.room_id
        await RoomWebsocketEventManager(room_id=room_id).async_send_event_to_group({'message': 'Hello from websocket!'})
        return EmptySchema()

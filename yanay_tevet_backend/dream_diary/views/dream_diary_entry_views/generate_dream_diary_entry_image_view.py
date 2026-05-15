from typing import Type

from ninja import Schema, Path

from dream_diary.managers.dream_diary_entry_manager import DreamDiaryEntryManager
from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from dream_diary.permissions_checkers.own_dream_diary_entry_permission_checker import OwnDreamDiaryEntryPermissionChecker
from dream_diary.serializers.dream_diary_entry_serializers.dream_diary_entry_serializer import DreamDiaryEntrySerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class GenerateDreamDiaryEntryImageView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return DreamDiaryEntrySerializer()

    @classmethod
    def get_model_cls(cls) -> Type:
        return DreamDiaryEntry

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: DreamDiaryEntry, data: Schema, path: Path) -> None:
        await OwnDreamDiaryEntryPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, obj: DreamDiaryEntry, data: Schema, path: Path) -> Schema | None:
        user = await request.future_user
        await DreamDiaryEntryManager(user).generate_image(obj)
        return None

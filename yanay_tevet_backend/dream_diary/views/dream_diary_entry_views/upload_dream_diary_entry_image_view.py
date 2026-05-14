from typing import Type

from ninja import Schema, Path, UploadedFile

from dream_diary.managers.dream_diary_entry_manager import DreamDiaryEntryManager
from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from dream_diary.permissions_checkers.own_dream_diary_entry_permission_checker import OwnDreamDiaryEntryPermissionChecker
from dream_diary.serializers.dream_diary_entry_serializers.dream_diary_entry_serializer import (
    DreamDiaryEntrySchema,
    DreamDiaryEntrySerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.views.upload_files_views.upload_files_by_id_view import UploadFilesByIdView
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath


class UploadDreamDiaryEntryImageView(UploadFilesByIdView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return DreamDiaryEntrySchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    def get_model_cls(cls) -> Type:
        return DreamDiaryEntry

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: DreamDiaryEntry | None, path: Path) -> None:
        await OwnDreamDiaryEntryPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def inner_run_action(cls, api_request: APIRequest, files: list[UploadedFile], obj: DreamDiaryEntry) -> DreamDiaryEntrySchema:
        user = await api_request.future_user
        await DreamDiaryEntryManager(user).upload_image(obj, files[0])
        return await DreamDiaryEntrySerializer().serialize(obj)

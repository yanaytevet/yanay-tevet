from typing import Type

from django.db.models import Model
from ninja import Schema, Path

from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from dream_diary.permissions_checkers.dream_diary_permission_checker import DreamDiaryPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteDreamDiaryEntryView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return DreamDiaryEntry

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        await DreamDiaryPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: DreamDiaryEntry, data: Schema, path: Path) -> None:
        user = await request.future_user
        if obj.user_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You do not own this entry.',
                error_code='not_owner',
            )

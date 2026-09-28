from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView
from special_dates.models.special_date import SpecialDate
from special_dates.permissions_checkers.special_date_member_permission_checker import SpecialDateMemberPermissionChecker


class DeleteSpecialDateView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDate

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SpecialDate, data: Schema, path: Path) -> None:
        await SpecialDateMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

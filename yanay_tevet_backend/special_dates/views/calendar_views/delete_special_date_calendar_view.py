from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.permissions_checkers.special_date_calendar_member_permission_checker import (
    SpecialDateCalendarMemberPermissionChecker,
)


class DeleteSpecialDateCalendarView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDateCalendar

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SpecialDateCalendar, data: Schema, path: Path) -> None:
        await SpecialDateCalendarMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

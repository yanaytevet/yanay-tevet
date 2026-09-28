import datetime
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.models.special_date import SpecialDate
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.permissions_checkers.special_date_member_permission_checker import SpecialDateMemberPermissionChecker
from special_dates.serializers.special_date_serializers.special_date_serializer import SpecialDateSerializer


class UpdateSpecialDateSchema(Schema):
    calendar_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[SpecialDateCategory] = None
    date: Optional[datetime.date] = None
    after_sunset: Optional[bool] = None
    input_calendar: Optional[CalendarType] = None
    remind_hebrew: Optional[bool] = None
    remind_gregorian: Optional[bool] = None


class UpdateSpecialDateView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateSpecialDateSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SpecialDateSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDate

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SpecialDate, data: UpdateSpecialDateSchema, path: Path) -> None:
        user = await request.future_user
        await SpecialDateMemberPermissionChecker(obj).async_raise_exception_if_not_valid(user)
        if data.calendar_id is not None and data.calendar_id != obj.calendar_id:
            await SpecialDateCalendarManager(user).get_member_calendar(data.calendar_id)

    @classmethod
    async def run_before_update(cls, request: APIRequest, obj: SpecialDate, data: UpdateSpecialDateSchema, path: Path) -> None:
        if data.calendar_id is not None and data.calendar_id != obj.calendar_id:
            target = await SpecialDateCalendarManager(await request.future_user).get_member_calendar(data.calendar_id)
            await SpecialDateManager.raise_if_calendar_full(target)

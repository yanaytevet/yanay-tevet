from datetime import date
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.schema_config import hidden_fields_config
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.models.special_date import SpecialDate
from special_dates.serializers.special_date_serializers.special_date_serializer import SpecialDateSerializer


class CreateSpecialDateSchema(Schema):
    model_config = hidden_fields_config('created_by_id')
    created_by_id: Optional[int] = None
    calendar_id: int
    name: str = Field(min_length=1, max_length=255)
    category: SpecialDateCategory
    date: date
    after_sunset: bool = False
    input_calendar: CalendarType = CalendarType.GREGORIAN
    remind_hebrew: bool = True
    remind_gregorian: bool = True


class CreateSpecialDateView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateSpecialDateSchema, path: Path) -> None:
        await SpecialDateCalendarManager(await request.future_user).get_member_calendar(data.calendar_id)

    @classmethod
    async def run_before_creation(cls, request: APIRequest, data: CreateSpecialDateSchema, path: Path) -> None:
        calendar = await SpecialDateCalendarManager(await request.future_user).get_member_calendar(data.calendar_id)
        await SpecialDateManager.raise_if_calendar_full(calendar)

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateSpecialDateSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SpecialDateSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDate

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateSpecialDateSchema, path: Path) -> CreateSpecialDateSchema:
        data.created_by_id = (await request.future_user).id
        return data

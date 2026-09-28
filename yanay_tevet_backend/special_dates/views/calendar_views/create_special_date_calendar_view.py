from typing import Type

from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.serializers.special_date_calendar_serializers.special_date_calendar_serializer import (
    SpecialDateCalendarSchema,
    SpecialDateCalendarSerializer,
)


class CreateSpecialDateCalendarSchema(Schema):
    name: str = Field(min_length=1, max_length=100)


class CreateSpecialDateCalendarView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return SpecialDateCalendarSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateSpecialDateCalendarSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, data: Schema = None, path: Path = None) -> None:
        pass

    @classmethod
    async def run_action(cls, api_request: APIRequest, data: CreateSpecialDateCalendarSchema, path: Path = None) -> SpecialDateCalendarSchema:
        user = await api_request.future_user
        calendar = await SpecialDateCalendarManager(user).create(data.name)
        return await SpecialDateCalendarSerializer(user).serialize(calendar)

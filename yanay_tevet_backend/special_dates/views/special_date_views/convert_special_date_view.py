import datetime
from typing import Optional, Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.enums.calendar_type import CalendarType
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.serializers.special_date_serializers.converted_date_serializer import (
    ConvertedDateSchema,
    ConvertedDateSerializer,
)
from special_dates.utils.hebrew_calendar import HebrewDate


class ConvertSpecialDateQuerySchema(Schema):
    calendar: CalendarType
    after_sunset: bool = False
    date: Optional[datetime.date] = None
    hebrew_year: Optional[int] = None
    hebrew_month: Optional[int] = None
    hebrew_day: Optional[int] = None


class ConvertSpecialDateView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ConvertedDateSchema

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return ConvertSpecialDateQuerySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: ConvertSpecialDateQuerySchema = None,
                       path: Path = None) -> ConvertedDateSchema:
        if query.calendar == CalendarType.GREGORIAN and query.date is not None:
            converted = SpecialDateManager.from_gregorian(query.date, query.after_sunset)
        elif (query.calendar == CalendarType.HEBREW and query.hebrew_year is not None
              and query.hebrew_month is not None and query.hebrew_day is not None):
            hebrew = HebrewDate(query.hebrew_year, query.hebrew_month, query.hebrew_day)
            converted = SpecialDateManager.from_hebrew(hebrew, query.after_sunset)
        else:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='חסר תאריך להמרה.',
                error_code='missing_date',
            )
        return await ConvertedDateSerializer().serialize(converted)

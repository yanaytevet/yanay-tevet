from datetime import date
from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.managers.special_date_manager import SpecialDateManager


class HebrewDateQuerySchema(Schema):
    date: date
    after_sunset: bool = False


class HebrewDateSchema(Schema):
    date: date
    after_sunset: bool
    hebrew_date: str


class GetHebrewDateView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return HebrewDateSchema

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return HebrewDateQuerySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: HebrewDateQuerySchema = None, path: Path = None) -> HebrewDateSchema:
        return HebrewDateSchema(
            date=query.date,
            after_sunset=query.after_sunset,
            hebrew_date=SpecialDateManager.format_hebrew_date(query.date, query.after_sunset),
        )

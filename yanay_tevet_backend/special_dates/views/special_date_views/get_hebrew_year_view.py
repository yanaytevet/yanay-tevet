from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.serializers.special_date_serializers.hebrew_year_serializer import (
    HebrewYearSchema,
    HebrewYearSerializer,
)


class HebrewYearQuerySchema(Schema):
    year: int


class GetHebrewYearView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return HebrewYearSchema

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return HebrewYearQuerySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: HebrewYearQuerySchema = None, path: Path = None) -> HebrewYearSchema:
        return await HebrewYearSerializer().serialize(query.year)

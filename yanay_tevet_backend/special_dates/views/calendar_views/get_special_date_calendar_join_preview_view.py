from typing import Type

from ninja import Path, Query, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.serializers.special_date_calendar_serializers.join_preview_serializer import (
    SpecialDateCalendarJoinPreviewSchema,
    SpecialDateCalendarJoinPreviewSerializer,
)


class JoinPreviewQuerySchema(Schema):
    token: str = Field(min_length=1, max_length=64)


class GetSpecialDateCalendarJoinPreviewView(SimpleGetAPIView):
    """Public: lets a logged-out visitor see which calendar a join link is for before signing in."""

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return SpecialDateCalendarJoinPreviewSchema

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return JoinPreviewQuerySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: JoinPreviewQuerySchema = None, path: Path = None) -> SpecialDateCalendarJoinPreviewSchema:
        calendar = await SpecialDateCalendarManager.get_by_join_token(query.token)
        return await SpecialDateCalendarJoinPreviewSerializer().serialize(calendar)

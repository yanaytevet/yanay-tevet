from typing import Type

from ninja import Schema, Query, Path

from dream_diary.managers.dream_diary_entry_manager import DreamDiaryEntryManager
from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class DreamDiaryCalendarSchema(Schema):
    logged_dates: list[str]


class GetDreamDiaryCalendarView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return DreamDiaryCalendarSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> DreamDiaryCalendarSchema:
        user = await api_request.future_user
        logged_dates = await DreamDiaryEntryManager(user).get_logged_dates_last_4_weeks()
        return DreamDiaryCalendarSchema(logged_dates=logged_dates)

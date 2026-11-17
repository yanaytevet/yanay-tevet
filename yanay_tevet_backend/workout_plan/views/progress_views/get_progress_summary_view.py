from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from workout_plan.managers.workout_progress_manager import WorkoutProgressManager
from workout_plan.serializers.progress_serializers.progress_schemas import ExerciseHistorySummarySchema


class ProgressSummarySchema(Schema):
    exercises: list[ExerciseHistorySummarySchema]


class GetProgressSummaryView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ProgressSummarySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ProgressSummarySchema:
        user = await api_request.future_user
        return ProgressSummarySchema(exercises=await WorkoutProgressManager(user).history_summary())

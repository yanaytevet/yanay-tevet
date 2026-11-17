from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from workout_plan.managers.exercise_manager import ExerciseManager
from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseSchema, ExerciseSerializer


class ExerciseListSchema(Schema):
    exercises: list[ExerciseSchema]


class ListExercisesView(SimpleGetAPIView):
    """The whole library the user can pick from. Small enough (tens of rows) to send at once."""

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ExerciseListSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ExerciseListSchema:
        user = await api_request.future_user
        exercises = ExerciseManager(user).visible_exercises()
        return ExerciseListSchema(exercises=await ExerciseSerializer().serialize_query(exercises))

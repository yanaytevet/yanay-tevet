from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from workout_plan.managers.workout_progress_manager import WorkoutProgressManager
from workout_plan.models.exercise import Exercise
from workout_plan.permissions_checkers.exercise_progress_permission_checker import ExerciseProgressPermissionChecker
from workout_plan.serializers.progress_serializers.progress_schemas import ExerciseProgressSchema


class ExerciseProgressPath(Schema):
    exercise_id: int


class GetExerciseProgressView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ExerciseProgressSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ExerciseProgressPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ExerciseProgressSchema:
        exercise = await Exercise.objects.filter(id=path.exercise_id).afirst()
        if exercise is None:
            raise ObjectDoesntExistAPIException(Exercise, path.exercise_id)
        user = await api_request.future_user
        await ExerciseProgressPermissionChecker(exercise).async_raise_exception_if_not_valid(user)
        return await WorkoutProgressManager(user).exercise_progress(exercise)

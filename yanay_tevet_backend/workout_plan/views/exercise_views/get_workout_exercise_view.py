from typing import Type

from django.db.models import Model
from ninja import Path, Query

from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.permissions_checkers.own_workout_routine_permission_checker import OwnWorkoutRoutinePermissionChecker
from workout_plan.serializers.workout_exercise_serializers.workout_exercise_serializer import WorkoutExerciseSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetWorkoutExerciseView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutExercise

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutExerciseSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutExercise, query: Query,
                                           path: Path) -> None:
        routine = await obj.get_routine()
        await OwnWorkoutRoutinePermissionChecker(routine).async_raise_exception_if_not_valid(await request.future_user)

from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.permissions_checkers.own_workout_routine_permission_checker import OwnWorkoutRoutinePermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteWorkoutExerciseView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutExercise

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutExercise, data: Schema,
                                           path: Path) -> None:
        routine = await obj.get_routine()
        await OwnWorkoutRoutinePermissionChecker(routine).async_raise_exception_if_not_valid(await request.future_user)

from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from workout_plan.managers.workout_exercise_manager import WorkoutExerciseManager
from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.permissions_checkers.own_workout_routine_permission_checker import OwnWorkoutRoutinePermissionChecker
from workout_plan.serializers.workout_exercise_serializers.workout_exercise_serializer import (
    WorkoutExerciseSerializer,
    WorkoutExerciseWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateWorkoutExerciseSchema(WorkoutExerciseWritableSchema):
    routine_id: int
    name: str


class CreateWorkoutExerciseView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateWorkoutExerciseSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutExerciseSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutExercise

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateWorkoutExerciseSchema,
                                              path: Path) -> None:
        routine = await WorkoutRoutine.objects.filter(id=data.routine_id).afirst()
        if routine is None:
            raise ObjectDoesntExistAPIException(WorkoutRoutine, data.routine_id)
        await OwnWorkoutRoutinePermissionChecker(routine).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateWorkoutExerciseSchema, path: Path) -> Model:
        user = await request.future_user
        writable = WorkoutExerciseWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'routine_id'})
        )
        return await WorkoutExerciseManager(user).create_exercise(data.routine_id, writable)

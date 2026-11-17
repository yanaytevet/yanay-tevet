from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.exercise_manager import ExerciseManager
from workout_plan.models.exercise import Exercise
from workout_plan.permissions_checkers.own_exercise_permission_checker import OwnExercisePermissionChecker
from workout_plan.serializers.exercise_serializers.exercise_serializer import (
    ExerciseSerializer,
    ExerciseWritableSchema,
)


class UpdateExerciseView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ExerciseWritableSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ExerciseSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Exercise

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Exercise, data: Schema, path: Path) -> None:
        await OwnExercisePermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: Exercise, data: ExerciseWritableSchema,
                            path: Path) -> None:
        await ExerciseManager(await request.future_user).update_custom(obj, data)

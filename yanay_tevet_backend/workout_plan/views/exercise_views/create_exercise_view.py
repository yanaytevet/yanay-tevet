from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.managers.exercise_manager import ExerciseManager
from workout_plan.models.exercise import Exercise
from workout_plan.serializers.exercise_serializers.exercise_serializer import (
    ExerciseSerializer,
    ExerciseWritableSchema,
)


class CreateExerciseView(CreateItemAPIView):
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
    async def check_permitted_before_creation(cls, request: APIRequest, data: ExerciseWritableSchema,
                                              path: Path) -> None:
        pass

    @classmethod
    async def create_object(cls, request: APIRequest, data: ExerciseWritableSchema, path: Path) -> Model:
        return await ExerciseManager(await request.future_user).create_custom(data)

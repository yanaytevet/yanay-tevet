from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from workout_plan.managers.workout_routine_manager import WorkoutRoutineManager
from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.serializers.workout_routine_serializers.workout_routine_serializer import WorkoutRoutineSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateWorkoutRoutineSchema(Schema):
    name: str


class CreateWorkoutRoutineView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateWorkoutRoutineSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutRoutineSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutRoutine

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateWorkoutRoutineSchema,
                                              path: Path) -> None:
        pass

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateWorkoutRoutineSchema, path: Path) -> Model:
        user = await request.future_user
        return await WorkoutRoutineManager(user).create_routine(data.name.strip())

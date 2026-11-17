from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.serializers.plan_serializers.workout_plan_detail_serializer import WorkoutPlanDetailSerializer


class CreateWorkoutPlanSchema(Schema):
    name: str
    pool_length_m: Optional[int] = None


class CreateWorkoutPlanView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateWorkoutPlanSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutPlanDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutPlan

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateWorkoutPlanSchema,
                                              path: Path) -> None:
        pass

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateWorkoutPlanSchema, path: Path) -> Model:
        return await WorkoutPlanManager(await request.future_user).create_plan(data.name, data.pool_length_m)

from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.plan_day_serializer import PlanDaySerializer


class CreatePlanDaySchema(Schema):
    plan_id: int
    name: str


class CreatePlanDayView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreatePlanDaySchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return PlanDaySerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return PlanDay

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreatePlanDaySchema,
                                              path: Path) -> None:
        if not await WorkoutPlan.objects.filter(id=data.plan_id).aexists():
            raise ObjectDoesntExistAPIException(WorkoutPlan, data.plan_id)
        await WorkoutPlanMemberPermissionChecker(data.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreatePlanDaySchema, path: Path) -> Model:
        plan = await WorkoutPlan.objects.aget(id=data.plan_id)
        return await WorkoutPlanManager(await request.future_user).add_day(plan, data.name)

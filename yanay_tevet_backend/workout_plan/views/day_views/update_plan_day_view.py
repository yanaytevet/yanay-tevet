from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.plan_day_serializer import PlanDaySerializer


class UpdatePlanDaySchema(Schema):
    name: str


class UpdatePlanDayView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdatePlanDaySchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return PlanDaySerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return PlanDay

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: PlanDay, data: Schema, path: Path) -> None:
        await WorkoutPlanMemberPermissionChecker(obj.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def update_object(cls, request: APIRequest, obj: PlanDay, data: UpdatePlanDaySchema, path: Path) -> None:
        await WorkoutPlanManager(await request.future_user).rename_day(obj, data.name)

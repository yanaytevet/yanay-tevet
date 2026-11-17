from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.workout_plan_detail_serializer import WorkoutPlanDetailSerializer


class UpdateWorkoutPlanSchema(Schema):
    name: Optional[str] = None
    pool_length_m: Optional[int] = None


class UpdateWorkoutPlanView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateWorkoutPlanSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutPlanDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutPlan

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutPlan, data: Schema,
                                           path: Path) -> None:
        await WorkoutPlanMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: WorkoutPlan, data: UpdateWorkoutPlanSchema,
                            path: Path) -> None:
        await WorkoutPlanManager(await request.future_user).update_plan(obj, data.name, data.pool_length_m)

from typing import Type

from django.db.models import Model
from ninja import Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.workout_plan_detail_serializer import WorkoutPlanDetailSerializer


class GetWorkoutPlanView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutPlan

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutPlanDetailSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutPlan, query: Query,
                                           path: Path) -> None:
        await WorkoutPlanMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

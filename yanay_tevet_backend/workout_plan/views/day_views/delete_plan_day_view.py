from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)


class DeletePlanDayView(DeleteItemByIdAPIView):
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
    async def run_before_deletion(cls, request: APIRequest, obj: PlanDay, data: Schema, path: Path) -> None:
        await WorkoutPlanManager(await request.future_user).ensure_day_deletable(obj)

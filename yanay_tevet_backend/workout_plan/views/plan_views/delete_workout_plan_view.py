from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)


class DeleteWorkoutPlanView(DeleteItemByIdAPIView):
    """Deleting a plan keeps everyone's logged sessions; they just lose the link to the plan."""

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutPlan

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutPlan, data: Schema,
                                           path: Path) -> None:
        await WorkoutPlanMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

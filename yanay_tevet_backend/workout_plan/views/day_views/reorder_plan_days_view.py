from typing import Type

from ninja import Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)


class ReorderPlanDaysPath(Schema):
    plan_id: int


class ReorderSchema(Schema):
    ordered_ids: list[int]


class ReorderResultSchema(Schema):
    success: bool


class ReorderPlanDaysView(SimplePostAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ReorderPlanDaysPath

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ReorderSchema

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ReorderResultSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ReorderSchema, path: ReorderPlanDaysPath = None) -> None:
        await WorkoutPlanMemberPermissionChecker(path.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, data: ReorderSchema,
                         path: ReorderPlanDaysPath = None) -> ReorderResultSchema:
        plan = await WorkoutPlan.objects.filter(id=path.plan_id).afirst()
        if plan is None:
            raise ObjectDoesntExistAPIException(WorkoutPlan, path.plan_id)
        await WorkoutPlanManager(await request.future_user).reorder_days(plan, data.ordered_ids)
        return ReorderResultSchema(success=True)

from typing import Type

from ninja import Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.views.day_views.reorder_plan_days_view import ReorderResultSchema, ReorderSchema


class ReorderPlanExercisesPath(Schema):
    day_id: int


class ReorderPlanExercisesView(SimplePostAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ReorderPlanExercisesPath

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ReorderSchema

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ReorderResultSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ReorderSchema,
                              path: ReorderPlanExercisesPath = None) -> None:
        day = await PlanDay.objects.filter(id=path.day_id).afirst()
        if day is None:
            raise ObjectDoesntExistAPIException(PlanDay, path.day_id)
        await WorkoutPlanMemberPermissionChecker(day.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, data: ReorderSchema,
                         path: ReorderPlanExercisesPath = None) -> ReorderResultSchema:
        day = await PlanDay.objects.aget(id=path.day_id)
        await WorkoutPlanManager(await request.future_user).reorder_exercises(day, data.ordered_ids)
        return ReorderResultSchema(success=True)

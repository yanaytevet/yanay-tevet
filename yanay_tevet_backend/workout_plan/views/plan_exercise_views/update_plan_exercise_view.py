from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import (
    PlanExerciseSerializer,
    PlanExerciseTargetsSchema,
)


class UpdatePlanExerciseView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return PlanExerciseTargetsSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return PlanExerciseSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return PlanExercise

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: PlanExercise, data: Schema,
                                           path: Path) -> None:
        day = await PlanDay.objects.aget(id=obj.day_id)
        await WorkoutPlanMemberPermissionChecker(day.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def update_object(cls, request: APIRequest, obj: PlanExercise, data: PlanExerciseTargetsSchema,
                            path: Path) -> None:
        await WorkoutPlanManager(await request.future_user).update_exercise(obj, data)

from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.managers.workout_session_manager import WorkoutSessionManager
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.session_serializers.workout_session_detail_serializer import (
    WorkoutSessionDetailSerializer,
)


class StartWorkoutSessionSchema(Schema):
    """A day of a plan, or only a plan (just the every-day section), or neither (a free workout)."""

    plan_id: Optional[int] = None
    day_id: Optional[int] = None


class StartWorkoutSessionView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return StartWorkoutSessionSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutSessionDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutSession

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: StartWorkoutSessionSchema,
                                              path: Path) -> None:
        user = await request.future_user
        plan_id = data.plan_id
        if data.day_id is not None:
            day = await PlanDay.objects.filter(id=data.day_id).afirst()
            if day is None:
                raise ObjectDoesntExistAPIException(PlanDay, data.day_id)
            plan_id = day.plan_id
        if plan_id is not None:
            await WorkoutPlanMemberPermissionChecker(plan_id).async_raise_exception_if_not_valid(user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: StartWorkoutSessionSchema, path: Path) -> Model:
        day = await PlanDay.objects.filter(id=data.day_id).afirst() if data.day_id is not None else None
        plan_id = day.plan_id if day is not None else data.plan_id
        plan = await WorkoutPlan.objects.filter(id=plan_id).afirst() if plan_id is not None else None
        if plan_id is not None and plan is None:
            raise ObjectDoesntExistAPIException(WorkoutPlan, plan_id)
        return await WorkoutSessionManager(await request.future_user).start(plan, day)

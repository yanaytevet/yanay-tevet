from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import (
    PlanExerciseSerializer,
    PlanExerciseTargetsSchema,
)


class CreatePlanExerciseSchema(PlanExerciseTargetsSchema):
    day_id: int
    exercise_id: int


class CreatePlanExerciseView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreatePlanExerciseSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return PlanExerciseSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return PlanExercise

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreatePlanExerciseSchema,
                                              path: Path) -> None:
        day = await PlanDay.objects.filter(id=data.day_id).afirst()
        if day is None:
            raise ObjectDoesntExistAPIException(PlanDay, data.day_id)
        await WorkoutPlanMemberPermissionChecker(day.plan_id).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreatePlanExerciseSchema, path: Path) -> Model:
        day = await PlanDay.objects.aget(id=data.day_id)
        exercise = await Exercise.objects.filter(id=data.exercise_id).afirst()
        if exercise is None:
            raise ObjectDoesntExistAPIException(Exercise, data.exercise_id)
        targets = PlanExerciseTargetsSchema(**data.model_dump(exclude_unset=True, exclude={'day_id', 'exercise_id'}))
        return await WorkoutPlanManager(await request.future_user).add_exercise(day, exercise, targets)

from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView
from workout_plan.enums.set_side import SetSide
from workout_plan.managers.workout_session_manager import WorkoutSessionManager
from workout_plan.models.exercise import Exercise
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.own_workout_session_permission_checker import (
    OwnWorkoutSessionPermissionChecker,
)
from workout_plan.serializers.session_serializers.set_log_serializer import SetLogSerializer, SetLogValuesSchema


class LogSetSchema(SetLogValuesSchema):
    session_id: int
    exercise_id: int
    plan_exercise_id: Optional[int] = None
    set_number: int
    side: SetSide = SetSide.BOTH


class LogSetView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return LogSetSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SetLogSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SetLog

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: LogSetSchema, path: Path) -> None:
        session = await WorkoutSession.objects.filter(id=data.session_id).afirst()
        if session is None:
            raise ObjectDoesntExistAPIException(WorkoutSession, data.session_id)
        await OwnWorkoutSessionPermissionChecker(session).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: LogSetSchema, path: Path) -> Model:
        session = await WorkoutSession.objects.aget(id=data.session_id)
        exercise = await Exercise.objects.filter(id=data.exercise_id).afirst()
        if exercise is None:
            raise ObjectDoesntExistAPIException(Exercise, data.exercise_id)
        values = SetLogValuesSchema(**data.model_dump(
            exclude_unset=True, exclude={'session_id', 'exercise_id', 'plan_exercise_id', 'set_number', 'side'},
        ))
        return await WorkoutSessionManager(await request.future_user).log_set(
            session, exercise, data.plan_exercise_id, data.set_number, data.side, values,
        )

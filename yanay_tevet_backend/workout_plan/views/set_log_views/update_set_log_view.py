from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.workout_session_manager import WorkoutSessionManager
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.own_workout_session_permission_checker import (
    OwnWorkoutSessionPermissionChecker,
)
from workout_plan.serializers.session_serializers.set_log_serializer import SetLogSerializer, SetLogValuesSchema


class UpdateSetLogView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return SetLogValuesSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SetLogSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SetLog

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SetLog, data: Schema, path: Path) -> None:
        session = await WorkoutSession.objects.aget(id=obj.session_id)
        await OwnWorkoutSessionPermissionChecker(session).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def update_object(cls, request: APIRequest, obj: SetLog, data: SetLogValuesSchema, path: Path) -> None:
        await WorkoutSessionManager(await request.future_user).update_set(obj, data)

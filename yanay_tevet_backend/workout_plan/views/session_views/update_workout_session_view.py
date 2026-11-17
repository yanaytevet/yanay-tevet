from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from workout_plan.managers.workout_session_manager import WorkoutSessionManager
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.own_workout_session_permission_checker import (
    OwnWorkoutSessionPermissionChecker,
)
from workout_plan.serializers.session_serializers.workout_session_detail_serializer import (
    WorkoutSessionDetailSerializer,
)


class UpdateWorkoutSessionSchema(Schema):
    finished: bool


class UpdateWorkoutSessionView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateWorkoutSessionSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutSessionDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutSession

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutSession, data: Schema,
                                           path: Path) -> None:
        await OwnWorkoutSessionPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: WorkoutSession, data: UpdateWorkoutSessionSchema,
                            path: Path) -> None:
        await WorkoutSessionManager(await request.future_user).set_finished(obj, data.finished)

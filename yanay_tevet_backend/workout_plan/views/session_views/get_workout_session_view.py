from typing import Type

from django.db.models import Model
from ninja import Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.own_workout_session_permission_checker import (
    OwnWorkoutSessionPermissionChecker,
)
from workout_plan.serializers.session_serializers.workout_session_detail_serializer import (
    WorkoutSessionDetailSerializer,
)


class GetWorkoutSessionView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutSession

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutSessionDetailSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutSession, query: Query,
                                           path: Path) -> None:
        await OwnWorkoutSessionPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

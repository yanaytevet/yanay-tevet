from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.own_workout_session_permission_checker import (
    OwnWorkoutSessionPermissionChecker,
)


class DeleteSetLogView(DeleteItemByIdAPIView):
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

from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.permissions_checkers.own_workout_routine_permission_checker import OwnWorkoutRoutinePermissionChecker
from workout_plan.serializers.workout_routine_serializers.workout_routine_serializer import WorkoutRoutineSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateWorkoutRoutineSchema(Schema):
    name: Optional[str] = None
    order: Optional[int] = None


class UpdateWorkoutRoutineView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateWorkoutRoutineSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutRoutineSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutRoutine

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: WorkoutRoutine, data: Schema,
                                           path: Path) -> None:
        await OwnWorkoutRoutinePermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

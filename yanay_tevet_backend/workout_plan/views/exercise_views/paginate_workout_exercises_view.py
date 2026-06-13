from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query, Schema

from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.permissions_checkers.own_workout_routine_permission_checker import OwnWorkoutRoutinePermissionChecker
from workout_plan.serializers.workout_exercise_serializers.workout_exercise_serializer import WorkoutExerciseSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class ExercisesByRoutinePath(Schema):
    routine_id: int


class PaginateWorkoutExercisesFilterSchema(FilterSchema):
    pass


class PaginateWorkoutExercisesView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ExercisesByRoutinePath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        routine = await WorkoutRoutine.objects.filter(id=path.routine_id).afirst()
        if routine is None:
            raise ObjectDoesntExistAPIException(WorkoutRoutine, path.routine_id)
        await OwnWorkoutRoutinePermissionChecker(routine).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutExerciseSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'order', 'name', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateWorkoutExercisesFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutExercise

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(routine_id=path.routine_id).order_by('order', 'id')

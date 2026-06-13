from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query

from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.serializers.workout_routine_serializers.workout_routine_serializer import WorkoutRoutineSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginateWorkoutRoutinesFilterSchema(FilterSchema):
    pass


class PaginateWorkoutRoutinesView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutRoutineSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'order', 'name', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateWorkoutRoutinesFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutRoutine

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(user_id=user.id).order_by('order', 'id')

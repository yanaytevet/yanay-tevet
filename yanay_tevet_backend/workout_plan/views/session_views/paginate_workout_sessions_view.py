from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.serializers.session_serializers.workout_session_serializer import WorkoutSessionSerializer


class PaginateWorkoutSessionsFilterSchema(FilterSchema):
    plan_id: int | None = None


class PaginateWorkoutSessionsView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutSessionSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'started_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateWorkoutSessionsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutSession

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(user_id=user.id).order_by('-started_at', '-id')

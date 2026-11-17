from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.serializers.plan_serializers.workout_plan_serializer import WorkoutPlanSerializer


class PaginateWorkoutPlansFilterSchema(FilterSchema):
    pass


class PaginateWorkoutPlansView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return WorkoutPlanSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'name', 'created_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateWorkoutPlansFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return WorkoutPlan

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(memberships__user=user).distinct().order_by('-updated_at')

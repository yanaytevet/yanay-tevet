from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query

from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.serializers.rental_project_serializers.rental_project_serializer import RentalProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginateRentalProjectsFilterSchema(FilterSchema):
    pass


class PaginateRentalProjectsView(PaginateItemsAPIView):
    @classmethod
    def get_project_app(cls) -> ProjectApp:
        return ProjectApp.APARTMENT_HUNT

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RentalProjectSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'name', 'created_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateRentalProjectsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return (
            queryset.filter(app=cls.get_project_app(), memberships__user=user)
            .distinct()
            .order_by('-updated_at')
        )

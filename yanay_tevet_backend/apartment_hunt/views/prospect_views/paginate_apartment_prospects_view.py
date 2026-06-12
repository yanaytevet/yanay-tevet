from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query, Schema

from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class ProspectsByProjectPath(Schema):
    project_id: int


class PaginateApartmentProspectsFilterSchema(FilterSchema):
    status: str | None = None


class PaginateApartmentProspectsView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ProspectsByProjectPath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        project = await RentalProject.objects.filter(id=path.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, path.project_id)
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ApartmentProspectSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'updated_at', 'liked_level', 'monthly_rent', 'status'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateApartmentProspectsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ApartmentProspect

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(project_id=path.project_id).order_by('-updated_at')

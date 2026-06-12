from typing import Type

from django.db.models import Model
from ninja import Path, Query

from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetApartmentProspectView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ApartmentProspect

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ApartmentProspectSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ApartmentProspect, query: Query, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

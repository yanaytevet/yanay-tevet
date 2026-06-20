from typing import Type

from django.db.models import Model
from ninja import Path, Query

from apartment_hunt.models.renter_prospect import RenterProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.renter_prospect_serializers.renter_prospect_serializer import (
    RenterProspectSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetRenterProspectView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RenterProspect

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RenterProspectSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RenterProspect, query: Query, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

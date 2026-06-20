from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.renter_prospect_manager import RenterProspectManager
from apartment_hunt.models.renter_prospect import RenterProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.renter_prospect_serializers.renter_prospect_serializer import (
    RenterProspectSerializer,
    RenterProspectWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateRenterProspectView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return RenterProspectWritableSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RenterProspectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RenterProspect

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RenterProspect, data: Schema, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: RenterProspect, data: RenterProspectWritableSchema, path: Path) -> None:
        user = await request.future_user
        writable = RenterProspectWritableSchema(**data.model_dump(exclude_unset=True))
        await RenterProspectManager(user).update_prospect(obj, writable)

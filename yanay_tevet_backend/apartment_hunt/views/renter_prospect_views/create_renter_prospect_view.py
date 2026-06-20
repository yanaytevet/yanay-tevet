from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.renter_prospect_manager import RenterProspectManager
from apartment_hunt.models.renter_prospect import RenterProspect
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.renter_prospect_serializers.renter_prospect_serializer import (
    RenterProspectSerializer,
    RenterProspectWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateRenterProspectSchema(RenterProspectWritableSchema):
    project_id: int


class CreateRenterProspectView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateRenterProspectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RenterProspectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RenterProspect

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateRenterProspectSchema, path: Path) -> None:
        project = await RentalProject.objects.filter(id=data.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, data.project_id)
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateRenterProspectSchema, path: Path) -> Model:
        user = await request.future_user
        writable = RenterProspectWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'project_id'})
        )
        return await RenterProspectManager(user).create_prospect(data.project_id, writable)

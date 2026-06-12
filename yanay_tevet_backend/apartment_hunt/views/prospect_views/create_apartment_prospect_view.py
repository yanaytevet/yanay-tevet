from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.apartment_prospect_manager import ApartmentProspectManager
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectSerializer,
    ApartmentProspectWritableSchema,
    ProspectContactInputSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateApartmentProspectSchema(ApartmentProspectWritableSchema):
    project_id: int
    contacts: list[ProspectContactInputSchema] = []


class CreateApartmentProspectView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateApartmentProspectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ApartmentProspectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ApartmentProspect

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateApartmentProspectSchema, path: Path) -> None:
        project = await RentalProject.objects.filter(id=data.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, data.project_id)
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateApartmentProspectSchema, path: Path) -> Model:
        user = await request.future_user
        writable = ApartmentProspectWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'project_id', 'contacts'})
        )
        return await ApartmentProspectManager(user).create_prospect(data.project_id, writable, data.contacts)

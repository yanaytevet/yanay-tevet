from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.apartment_prospect_manager import ApartmentProspectManager
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectSerializer,
    ApartmentProspectWritableSchema,
    ProspectContactInputSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateApartmentProspectSchema(ApartmentProspectWritableSchema):
    contacts: Optional[list[ProspectContactInputSchema]] = None


class UpdateApartmentProspectView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateApartmentProspectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ApartmentProspectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ApartmentProspect

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ApartmentProspect, data: Schema, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: ApartmentProspect, data: UpdateApartmentProspectSchema, path: Path) -> None:
        user = await request.future_user
        writable = ApartmentProspectWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'contacts'})
        )
        contacts = data.contacts if 'contacts' in data.model_fields_set else None
        await ApartmentProspectManager(user).update_prospect(obj, writable, contacts)

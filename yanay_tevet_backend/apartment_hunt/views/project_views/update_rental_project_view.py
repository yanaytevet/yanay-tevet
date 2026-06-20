from decimal import Decimal
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.enums.currency import Currency
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.rental_project_serializers.rental_project_serializer import RentalProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateRentalProjectSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[Currency] = None
    initial_asked_rent: Optional[Decimal] = None


class UpdateRentalProjectView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateRentalProjectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RentalProjectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RentalProject, data: Schema, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.unit_manager import UnitManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.models.unit import Unit
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.unit_serializers.unit_serializer import UnitSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateUnitSchema(Schema):
    project_id: int
    name: str
    description: str = ''


class CreateUnitView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateUnitSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return UnitSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Unit

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateUnitSchema, path: Path) -> None:
        project = await RentalProject.objects.filter(id=data.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, data.project_id)
        await ProjectMemberPermissionChecker(project, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateUnitSchema, path: Path) -> Model:
        user = await request.future_user
        return await UnitManager(user).create_unit(data.project_id, data.name, data.description)

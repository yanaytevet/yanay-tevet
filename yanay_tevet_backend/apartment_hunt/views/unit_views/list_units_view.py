from typing import Type

from ninja import Path, Query, Schema

from apartment_hunt.managers.unit_manager import UnitManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.unit_serializers.unit_serializer import UnitSchema, UnitSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class UnitsListSchema(Schema):
    units: list[UnitSchema]


class ListUnitsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UnitsListSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> UnitsListSchema:
        project = await RentalProject.objects.filter(id=path.object_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, path.object_id)
        user = await api_request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)
        units = await UnitManager(user).list_units(project)
        serializer = UnitSerializer()
        return UnitsListSchema(units=[await serializer.serialize(u) for u in units])

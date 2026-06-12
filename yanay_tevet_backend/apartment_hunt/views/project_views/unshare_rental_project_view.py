from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.rental_project_manager import RentalProjectManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.rental_project_serializers.rental_project_serializer import RentalProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class UnshareRentalProjectSchema(Schema):
    username: str


class UnshareRentalProjectView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RentalProjectSerializer()

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UnshareRentalProjectSchema

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RentalProject, data: Schema, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, obj: RentalProject, data: UnshareRentalProjectSchema, path: Path) -> None:
        user = await request.future_user
        await RentalProjectManager(user).unshare(obj, data.username)
        return None

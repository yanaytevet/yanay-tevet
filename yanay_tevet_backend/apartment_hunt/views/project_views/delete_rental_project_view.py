from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteRentalProjectView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RentalProject, data: Schema, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

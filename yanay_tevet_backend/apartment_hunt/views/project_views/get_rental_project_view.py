from typing import Type

from django.db.models import Model
from ninja import Path, Query

from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.rental_project_serializers.rental_project_serializer import RentalProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetRentalProjectView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RentalProjectSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: RentalProject, query: Query, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

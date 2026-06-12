from typing import Type

from ninja import Path, Schema, UploadedFile

from apartment_hunt.managers.apartment_prospect_manager import ApartmentProspectManager
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectSchema,
    ApartmentProspectSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.upload_files_views.upload_files_by_id_view import UploadFilesByIdView


class UploadApartmentProspectImageView(UploadFilesByIdView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ApartmentProspectSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    def get_model_cls(cls) -> Type:
        return ApartmentProspect

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ApartmentProspect | None, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def inner_run_action(cls, api_request: APIRequest, files: list[UploadedFile], obj: ApartmentProspect) -> ApartmentProspectSchema:
        user = await api_request.future_user
        await ApartmentProspectManager(user).add_image(obj, files[0])
        return await ApartmentProspectSerializer().serialize(obj)

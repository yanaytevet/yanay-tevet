from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.models.apartment_image import ApartmentImage
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteApartmentImageView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ApartmentImage

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ApartmentImage, data: Schema, path: Path) -> None:
        prospect = await ApartmentProspect.objects.filter(id=obj.prospect_id).afirst()
        project = await prospect.get_project() if prospect else None
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteItineraryListView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        await ListMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

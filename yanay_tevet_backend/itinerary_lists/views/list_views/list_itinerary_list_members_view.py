from typing import Type

from ninja import Path, Query, Schema

from itinerary_lists.managers.itinerary_list_manager import ItineraryListManager
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.list_membership_serializers.list_membership_serializer import (
    ListMembershipSchema,
    ListMembershipSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class ListMembersSchema(Schema):
    members: list[ListMembershipSchema]


class ListItineraryListMembersView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ListMembersSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ListMembersSchema:
        itinerary_list = await ItineraryList.objects.filter(id=path.object_id).afirst()
        if itinerary_list is None:
            raise ObjectDoesntExistAPIException(ItineraryList, path.object_id)
        user = await api_request.future_user
        await ListMemberPermissionChecker(itinerary_list).async_raise_exception_if_not_valid(user)
        memberships = await ItineraryListManager(user).list_members(itinerary_list)
        serializer = ListMembershipSerializer()
        members = [await serializer.serialize(m) for m in memberships]
        return ListMembersSchema(members=members)

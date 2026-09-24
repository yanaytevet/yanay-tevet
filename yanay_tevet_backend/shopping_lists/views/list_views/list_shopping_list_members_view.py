from typing import Type

from ninja import Path, Query, Schema

from shopping_lists.managers.shopping_list_manager import ShoppingListManager
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_list_membership_serializers.shopping_list_membership_serializer import (
    ShoppingListMembershipSchema,
    ShoppingListMembershipSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.serializers.invitation.pending_invitation_serializer import (
    PendingInvitationSchema,
    PendingInvitationSerializer,
)


class ShoppingListMembersSchema(Schema):
    members: list[ShoppingListMembershipSchema]
    pending_invitations: list[PendingInvitationSchema]


class ListShoppingListMembersView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ShoppingListMembersSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ShoppingListMembersSchema:
        shopping_list = await ShoppingList.objects.filter(id=path.object_id).afirst()
        if shopping_list is None:
            raise ObjectDoesntExistAPIException(ShoppingList, path.object_id)
        user = await api_request.future_user
        await ShoppingListMemberPermissionChecker(shopping_list).async_raise_exception_if_not_valid(user)
        manager = ShoppingListManager(user)
        member_serializer = ShoppingListMembershipSerializer()
        members = [await member_serializer.serialize(m) for m in await manager.list_members(shopping_list)]
        pending_serializer = PendingInvitationSerializer()
        pending_invitations = [
            await pending_serializer.serialize(p) for p in await manager.list_pending_invitations(shopping_list)
        ]
        return ShoppingListMembersSchema(members=members, pending_invitations=pending_invitations)

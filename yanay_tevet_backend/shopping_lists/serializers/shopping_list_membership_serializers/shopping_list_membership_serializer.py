from ninja import Schema

from shopping_lists.enums.shopping_list_role import ShoppingListRole
from shopping_lists.models.shopping_list_membership import ShoppingListMembership
from common.simple_api.serializers.serializer import Serializer


class ShoppingListMembershipSchema(Schema):
    id: int
    user_id: int
    username: str
    full_name: str
    role: ShoppingListRole


class ShoppingListMembershipSerializer(Serializer[ShoppingListMembershipSchema]):
    async def inner_serialize(self, obj: ShoppingListMembership) -> ShoppingListMembershipSchema:
        member = await obj.get_user()
        return ShoppingListMembershipSchema(
            id=obj.id,
            user_id=obj.user_id,
            username=member.username if member else '',
            full_name=member.get_full_name() if member else '',
            role=ShoppingListRole(obj.role),
        )

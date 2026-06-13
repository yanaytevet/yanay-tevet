from ninja import Schema

from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from common.simple_api.serializers.serializer import Serializer


class ListMembershipSchema(Schema):
    id: int
    user_id: int
    username: str
    full_name: str
    role: ListRole


class ListMembershipSerializer(Serializer[ListMembershipSchema]):
    async def inner_serialize(self, obj: ItineraryListMembership) -> ListMembershipSchema:
        member = await obj.get_user()
        return ListMembershipSchema(
            id=obj.id,
            user_id=obj.user_id,
            username=member.username if member else '',
            full_name=member.get_full_name() if member else '',
            role=ListRole(obj.role),
        )

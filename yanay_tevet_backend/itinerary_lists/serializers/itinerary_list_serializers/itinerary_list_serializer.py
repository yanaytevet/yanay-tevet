from datetime import datetime
from typing import Optional

from ninja import Schema

from itinerary_lists.enums.list_status import ListStatus
from itinerary_lists.models.itinerary_list import ItineraryList
from common.simple_api.serializers.serializer import Serializer


class ItineraryListSchema(Schema):
    id: int
    name: str
    description: str
    status: ListStatus
    owner_id: int
    owner_username: str
    member_count: int
    item_count: int
    task_count: int
    activated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ItineraryListSerializer(Serializer[ItineraryListSchema]):
    async def inner_serialize(self, obj: ItineraryList) -> ItineraryListSchema:
        owner = await obj.get_owner()
        member_count = await obj.memberships.acount()
        item_count = await obj.items.acount()
        task_count = await obj.tasks.acount()
        return ItineraryListSchema(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            status=ListStatus(obj.status),
            owner_id=obj.owner_id,
            owner_username=owner.username if owner else '',
            member_count=member_count,
            item_count=item_count,
            task_count=task_count,
            activated_at=obj.activated_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

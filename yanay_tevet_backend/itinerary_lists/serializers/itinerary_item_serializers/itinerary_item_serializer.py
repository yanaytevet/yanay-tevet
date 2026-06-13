from datetime import datetime
from typing import Optional

from ninja import Schema

from itinerary_lists.enums.item_status import ItemStatus
from itinerary_lists.models.itinerary_item import ItineraryItem
from common.simple_api.serializers.serializer import Serializer


class ItineraryItemSchema(Schema):
    id: int
    itinerary_list_id: int
    name: str
    description: str
    status: ItemStatus
    order: int
    created_at: datetime
    updated_at: datetime


class ItineraryItemWritableSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    order: Optional[int] = None


class ItineraryItemSerializer(Serializer[ItineraryItemSchema]):
    async def inner_serialize(self, obj: ItineraryItem) -> ItineraryItemSchema:
        return ItineraryItemSchema(
            id=obj.id,
            itinerary_list_id=obj.itinerary_list_id,
            name=obj.name,
            description=obj.description,
            status=ItemStatus(obj.status),
            order=obj.order,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

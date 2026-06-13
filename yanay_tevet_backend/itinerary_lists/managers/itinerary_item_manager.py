from django.db.models import Max

from itinerary_lists.models.itinerary_item import ItineraryItem
from itinerary_lists.serializers.itinerary_item_serializers.itinerary_item_serializer import (
    ItineraryItemWritableSchema,
)
from common.django_utils.model_utils import ModelUtils
from users.models import User


class ItineraryItemManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_item(self, itinerary_list_id: int, writable: ItineraryItemWritableSchema) -> ItineraryItem:
        next_order = await self._next_order(itinerary_list_id)
        item = ItineraryItem(
            itinerary_list_id=itinerary_list_id,
            created_by_id=self.user.id,
            order=next_order,
        )
        await ModelUtils.update_from_schema(item, writable)
        await item.asave()
        return item

    async def update_item(self, item: ItineraryItem, writable: ItineraryItemWritableSchema) -> None:
        await ModelUtils.update_from_schema(item, writable)
        await item.asave()

    async def _next_order(self, itinerary_list_id: int) -> int:
        aggregate = await ItineraryItem.objects.filter(
            itinerary_list_id=itinerary_list_id
        ).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1

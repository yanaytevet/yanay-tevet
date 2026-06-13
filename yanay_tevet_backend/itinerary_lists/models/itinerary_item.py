from typing import TYPE_CHECKING

from django.db import models

from itinerary_lists.enums.item_status import ItemStatus
from itinerary_lists.models.itinerary_list import ItineraryList
from users.models import User


class ItineraryItem(models.Model):
    if TYPE_CHECKING:
        id: int
        itinerary_list_id: int
        created_by_id: int

    list_display = ['id', 'name', 'itinerary_list', 'status', 'order', 'updated_at']
    list_filter = ['status']
    raw_id_fields = ['itinerary_list', 'created_by']

    itinerary_list = models.ForeignKey(ItineraryList, on_delete=models.CASCADE, related_name='items')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_itinerary_items')

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status: ItemStatus = models.CharField(
        max_length=16,
        choices=ItemStatus.choices(),
        default=ItemStatus.NEED_TO_BUY,
        blank=True,
    )
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'ItineraryItem({self.id}) - {self.name}'

    async def get_itinerary_list(self) -> ItineraryList | None:
        return await ItineraryList.objects.filter(id=self.itinerary_list_id).afirst()

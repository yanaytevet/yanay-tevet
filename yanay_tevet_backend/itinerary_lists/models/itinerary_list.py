from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from itinerary_lists.enums.list_status import ListStatus
from users.models import User

if TYPE_CHECKING:
    from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
    from itinerary_lists.models.itinerary_item import ItineraryItem
    from itinerary_lists.models.itinerary_task import ItineraryTask


class ItineraryList(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        memberships: Manager['ItineraryListMembership']
        items: Manager['ItineraryItem']
        tasks: Manager['ItineraryTask']

    list_display = ['id', 'name', 'owner', 'status', 'activated_at', 'updated_at']
    list_filter = ['status']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_itinerary_lists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status: ListStatus = models.CharField(
        max_length=16,
        choices=ListStatus.choices(),
        default=ListStatus.STANDBY,
        blank=True,
    )
    activated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'ItineraryList({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()

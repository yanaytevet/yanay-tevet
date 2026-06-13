from typing import TYPE_CHECKING

from django.db import models

from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.models.itinerary_list import ItineraryList
from users.models import User


class ItineraryListMembership(models.Model):
    if TYPE_CHECKING:
        id: int
        itinerary_list_id: int
        user_id: int

    list_display = ['id', 'itinerary_list', 'user', 'role', 'created_at']
    list_filter = ['role']
    raw_id_fields = ['itinerary_list', 'user']

    itinerary_list = models.ForeignKey(ItineraryList, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itinerary_list_memberships')
    role: ListRole = models.CharField(
        max_length=16,
        choices=ListRole.choices(),
        default=ListRole.COLLABORATOR,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['itinerary_list', 'user'], name='unique_itinerary_list_membership'),
        ]
        ordering = ['id']

    def __str__(self) -> str:
        return f'ItineraryListMembership({self.id}) - list={self.itinerary_list_id} user={self.user_id} ({self.role})'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()

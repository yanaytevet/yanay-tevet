import secrets
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from users.models import User

if TYPE_CHECKING:
    from special_dates.models.special_date import SpecialDate
    from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership


def generate_join_token() -> str:
    return secrets.token_urlsafe(24)


class SpecialDateCalendar(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        memberships: Manager['SpecialDateCalendarMembership']
        special_dates: Manager['SpecialDate']

    list_display = ['id', 'name', 'owner', 'updated_at']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_special_date_calendars')
    name = models.CharField(max_length=100)
    # Long-lived: anyone logged in who opens the join link becomes an editor. The owner can reset it.
    join_token = models.CharField(max_length=64, unique=True, default=generate_join_token)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self) -> str:
        return f'SpecialDateCalendar({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()

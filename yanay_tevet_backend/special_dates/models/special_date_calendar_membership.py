from typing import TYPE_CHECKING

from django.db import models

from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.models.special_date_calendar import SpecialDateCalendar
from users.models import User


class SpecialDateCalendarMembership(models.Model):
    if TYPE_CHECKING:
        id: int
        calendar_id: int
        user_id: int

    list_display = ['id', 'calendar', 'user', 'role']
    raw_id_fields = ['calendar', 'user']

    calendar = models.ForeignKey(SpecialDateCalendar, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='special_date_calendar_memberships')
    role = models.CharField(max_length=16, choices=SpecialDateCalendarRole.choices(), default=SpecialDateCalendarRole.EDITOR)
    hide_from_upcoming = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
        constraints = [models.UniqueConstraint(fields=['calendar', 'user'], name='unique_special_date_calendar_member')]

    def __str__(self) -> str:
        return f'SpecialDateCalendarMembership({self.id}) - calendar {self.calendar_id} user {self.user_id}'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()

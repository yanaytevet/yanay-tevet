from typing import TYPE_CHECKING

from django.db import models

from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.models.special_date_calendar import SpecialDateCalendar
from users.models import User


class SpecialDate(models.Model):
    if TYPE_CHECKING:
        id: int
        created_by_id: int | None
        calendar_id: int | None

    list_display = ['id', 'name', 'date', 'category', 'calendar', 'created_by']
    raw_id_fields = ['created_by', 'calendar']

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_special_dates')
    # Nullable only so events from before calendars existed can be attached lazily (SpecialDateCalendarManager).
    calendar = models.ForeignKey(SpecialDateCalendar, on_delete=models.CASCADE, null=True, blank=True, related_name='special_dates')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=SpecialDateCategory.choices(), default=SpecialDateCategory.BIRTHDAY)
    # Always stored as the Gregorian date; `after_sunset` means between sunset and midnight, so the Hebrew day is the next one.
    date = models.DateField()
    after_sunset = models.BooleanField(default=False)
    input_calendar = models.CharField(max_length=16, choices=CalendarType.choices(), default=CalendarType.GREGORIAN)
    remind_hebrew = models.BooleanField(default=True)
    remind_gregorian = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'id']
        indexes = [models.Index(fields=['calendar', 'name'])]

    def __str__(self) -> str:
        return f'SpecialDate({self.id}) - {self.name} ({self.date})'

    async def get_created_by(self) -> User | None:
        if self.created_by_id is None:
            return None
        if SpecialDate.created_by.is_cached(self):
            return self.created_by
        return await User.objects.filter(id=self.created_by_id).afirst()

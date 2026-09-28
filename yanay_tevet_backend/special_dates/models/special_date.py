from typing import TYPE_CHECKING

from django.db import models

from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_category import SpecialDateCategory
from users.models import User


class SpecialDate(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int

    list_display = ['id', 'name', 'date', 'category', 'owner']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='special_dates')
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
        indexes = [models.Index(fields=['owner', 'name'])]

    def __str__(self) -> str:
        return f'SpecialDate({self.id}) - {self.name} ({self.date})'

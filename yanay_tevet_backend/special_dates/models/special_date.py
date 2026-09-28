from typing import TYPE_CHECKING

from django.db import models

from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.enums.special_date_recurrence import SpecialDateRecurrence
from users.models import User


class SpecialDate(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int

    list_display = ['id', 'description', 'date', 'category', 'owner']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='special_dates')
    date = models.DateField()
    after_sunset = models.BooleanField(default=False)
    category = models.CharField(max_length=32, choices=SpecialDateCategory.choices(), default=SpecialDateCategory.BIRTHDAY)
    recurrence = models.CharField(max_length=16, choices=SpecialDateRecurrence.choices(), default=SpecialDateRecurrence.BOTH)
    description = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'id']
        indexes = [models.Index(fields=['owner', 'date'])]

    def __str__(self) -> str:
        return f'SpecialDate({self.id}) - {self.description} ({self.date})'

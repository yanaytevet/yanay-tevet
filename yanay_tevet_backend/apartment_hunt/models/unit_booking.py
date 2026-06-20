from typing import TYPE_CHECKING

from django.db import models

from apartment_hunt.models.unit import Unit
from users.models import User


class UnitBooking(models.Model):
    if TYPE_CHECKING:
        id: int
        unit_id: int
        created_by_id: int

    list_display = ['id', 'unit', 'created_by', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date']
    raw_id_fields = ['unit', 'created_by']

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='bookings')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='unit_bookings'
    )

    # A booking occupies the nights [start_date, end_date): check-in inclusive,
    # check-out exclusive, so one guest's check-out day can be another's check-in.
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date', 'id']

    def __str__(self) -> str:
        return f'UnitBooking({self.id}) - unit={self.unit_id} {self.start_date}..{self.end_date}'

    async def get_unit(self) -> Unit | None:
        return await Unit.objects.filter(id=self.unit_id).afirst()

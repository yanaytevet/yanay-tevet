from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from apartment_hunt.models.rental_project import RentalProject

if TYPE_CHECKING:
    from apartment_hunt.models.unit_booking import UnitBooking


class Unit(models.Model):
    if TYPE_CHECKING:
        id: int
        project_id: int
        bookings: Manager['UnitBooking']

    list_display = ['id', 'name', 'project', 'created_at']
    raw_id_fields = ['project']

    project = models.ForeignKey(RentalProject, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'Unit({self.id}) - {self.name}'

    async def get_project(self) -> RentalProject | None:
        return await RentalProject.objects.filter(id=self.project_id).afirst()

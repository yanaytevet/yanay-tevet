from typing import TYPE_CHECKING

from django.db import models

from apartment_hunt.enums.family_status import FamilyStatus
from apartment_hunt.enums.renter_status import RenterStatus
from apartment_hunt.models.rental_project import RentalProject
from users.models import User


class RenterProspect(models.Model):
    if TYPE_CHECKING:
        id: int
        project_id: int
        created_by_id: int

    list_display = ['id', 'name', 'project', 'status', 'family_status', 'agreed_rent', 'updated_at']
    list_filter = ['status', 'family_status', 'has_animals', 'long_term', 'saw_apartment']
    raw_id_fields = ['project', 'created_by']

    project = models.ForeignKey(RentalProject, on_delete=models.CASCADE, related_name='renter_prospects')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_renter_prospects'
    )

    name = models.CharField(max_length=255)
    status: RenterStatus = models.CharField(
        max_length=32,
        choices=RenterStatus.choices(),
        default=RenterStatus.CONTACTED,
        blank=True,
    )

    saw_apartment = models.BooleanField(default=False, blank=True)
    visit_time = models.DateTimeField(null=True, blank=True)

    has_animals = models.BooleanField(default=False, blank=True)
    long_term = models.BooleanField(default=False, blank=True)
    family_status: FamilyStatus = models.CharField(
        max_length=32,
        choices=FamilyStatus.choices(),
        default=FamilyStatus.SINGLE,
        blank=True,
    )

    notes = models.TextField(blank=True, default='')
    agreed_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'RenterProspect({self.id}) - {self.name or "unnamed"}'

    async def get_project(self) -> RentalProject | None:
        return await RentalProject.objects.filter(id=self.project_id).afirst()

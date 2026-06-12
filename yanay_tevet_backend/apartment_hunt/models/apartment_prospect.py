from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from apartment_hunt.enums.prospect_status import ProspectStatus
from apartment_hunt.models.rental_project import RentalProject
from users.models import User

if TYPE_CHECKING:
    from apartment_hunt.models.apartment_image import ApartmentImage
    from apartment_hunt.models.prospect_contact import ProspectContact


class ApartmentProspect(models.Model):
    if TYPE_CHECKING:
        id: int
        project_id: int
        created_by_id: int
        images: Manager['ApartmentImage']
        contacts: Manager['ProspectContact']

    list_display = ['id', 'title', 'project', 'status', 'town', 'monthly_rent', 'updated_at']
    list_filter = ['status', 'via_agency', 'has_protected_room']
    raw_id_fields = ['project', 'created_by']

    project = models.ForeignKey(RentalProject, on_delete=models.CASCADE, related_name='prospects')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_prospects')

    title = models.CharField(max_length=255, blank=True, default='')
    status: ProspectStatus = models.CharField(
        max_length=32,
        choices=ProspectStatus.choices(),
        default=ProspectStatus.SAW,
        blank=True,
    )

    town = models.CharField(max_length=255, blank=True, default='')
    full_address = models.CharField(max_length=512, blank=True, default='')

    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    via_agency = models.BooleanField(default=False, blank=True)
    agency_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_tax_benefit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    has_protected_room = models.BooleanField(default=False, blank=True)
    liked_level = models.PositiveSmallIntegerField(null=True, blank=True)

    rooms = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    size_sqm = models.IntegerField(null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)

    listing_url = models.CharField(max_length=1024, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'ApartmentProspect({self.id}) - {self.title or self.full_address or "untitled"}'

    async def get_project(self) -> RentalProject | None:
        return await RentalProject.objects.filter(id=self.project_id).afirst()

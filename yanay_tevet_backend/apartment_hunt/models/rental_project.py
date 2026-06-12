from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from apartment_hunt.enums.currency import Currency
from users.models import User

if TYPE_CHECKING:
    from apartment_hunt.models.project_membership import ProjectMembership
    from apartment_hunt.models.apartment_prospect import ApartmentProspect


class RentalProject(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        memberships: Manager['ProjectMembership']
        prospects: Manager['ApartmentProspect']

    list_display = ['id', 'name', 'owner', 'currency', 'updated_at']
    list_filter = ['currency']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_rental_projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    currency: Currency = models.CharField(
        max_length=8,
        choices=Currency.choices(),
        default=Currency.NIS,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'RentalProject({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()

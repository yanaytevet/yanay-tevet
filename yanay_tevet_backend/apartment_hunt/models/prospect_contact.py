from typing import TYPE_CHECKING

from django.db import models

from apartment_hunt.enums.contact_method import ContactMethod
from apartment_hunt.models.apartment_prospect import ApartmentProspect


class ProspectContact(models.Model):
    if TYPE_CHECKING:
        id: int
        prospect_id: int

    list_display = ['id', 'prospect', 'method', 'value', 'label', 'order']
    list_filter = ['method']
    raw_id_fields = ['prospect']

    prospect = models.ForeignKey(ApartmentProspect, on_delete=models.CASCADE, related_name='contacts')
    method: ContactMethod = models.CharField(
        max_length=16,
        choices=ContactMethod.choices(),
        default=ContactMethod.OTHER,
        blank=True,
    )
    value = models.CharField(max_length=512, blank=True, default='')
    label = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'ProspectContact({self.id}) - {self.method}: {self.value}'

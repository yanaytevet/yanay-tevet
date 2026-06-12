from typing import TYPE_CHECKING

from django.db import models

from apartment_hunt.models.apartment_prospect import ApartmentProspect


class ApartmentImage(models.Model):
    if TYPE_CHECKING:
        id: int
        prospect_id: int

    list_display = ['id', 'prospect', 'image_url', 'order', 'created_at']
    list_filter = []
    raw_id_fields = ['prospect']

    prospect = models.ForeignKey(ApartmentProspect, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=1024)
    caption = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'ApartmentImage({self.id}) - prospect={self.prospect_id}'

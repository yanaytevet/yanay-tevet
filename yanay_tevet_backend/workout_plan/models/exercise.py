from typing import TYPE_CHECKING

from django.db import models

from users.models import User
from workout_plan.enums.muscle_group import MuscleGroup
from workout_plan.enums.tracking_type import TrackingType


class Exercise(models.Model):
    """A library exercise. owner is None for the built-in catalog; otherwise it is a user's own."""

    if TYPE_CHECKING:
        id: int
        owner_id: int | None

    list_display = ['id', 'name_en', 'name_he', 'muscle_group', 'tracking_type', 'per_side', 'owner']
    list_filter = ['muscle_group', 'tracking_type']
    search_fields = ['name_en', 'name_he', 'catalog_key']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workout_exercises')
    # Stable id of a built-in exercise, so the catalog seed can be re-run without duplicating rows.
    catalog_key = models.CharField(max_length=64, null=True, blank=True, unique=True)
    name_en = models.CharField(max_length=255, blank=True, default='')
    name_he = models.CharField(max_length=255, blank=True, default='')
    # The other site languages' names, {language code: name}. Filled for the built-in catalog only
    # (catalog/exercise_name_translations.py); a user's own exercise has just the names they typed.
    name_translations = models.JSONField(default=dict, blank=True)
    muscle_group: MuscleGroup = models.CharField(
        max_length=16, choices=MuscleGroup.choices(), default=MuscleGroup.OTHER, blank=True,
    )
    tracking_type: TrackingType = models.CharField(
        max_length=16, choices=TrackingType.choices(), default=TrackingType.WEIGHT_REPS, blank=True,
    )
    per_side = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['muscle_group', 'name_en', 'id']

    def __str__(self) -> str:
        return f'Exercise({self.id}) - {self.name_en or self.name_he}'

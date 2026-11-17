from typing import TYPE_CHECKING

from django.db import models

from users.models import User
from workout_plan.enums.workout_language import WorkoutLanguage


class WorkoutPreferences(models.Model):
    if TYPE_CHECKING:
        id: int
        user_id: int

    list_display = ['id', 'user', 'language']
    raw_id_fields = ['user']

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='workout_preferences')
    language: WorkoutLanguage = models.CharField(
        max_length=4, choices=WorkoutLanguage.choices(), default=WorkoutLanguage.HEBREW, blank=True,
    )

    def __str__(self) -> str:
        return f'WorkoutPreferences({self.id}) - user {self.user_id} ({self.language})'

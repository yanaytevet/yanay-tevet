from typing import TYPE_CHECKING

from django.db import models

from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_day import PlanDay


class PlanExercise(models.Model):
    """An exercise on a day of a plan, with its targets. Only the targets that fit the exercise's tracking
    type are used; a missing target reps means 'as many as possible'."""

    if TYPE_CHECKING:
        id: int
        day_id: int
        exercise_id: int

    list_display = ['id', 'day', 'exercise', 'order', 'target_sets', 'target_reps', 'target_weight_kg']
    raw_id_fields = ['day', 'exercise']

    day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='plan_entries')
    order = models.PositiveIntegerField(default=0, blank=True)

    target_sets = models.PositiveIntegerField(default=3, blank=True)
    target_reps = models.PositiveIntegerField(null=True, blank=True)
    target_weight_kg = models.FloatField(null=True, blank=True)
    target_seconds = models.PositiveIntegerField(null=True, blank=True)
    target_distance_km = models.FloatField(null=True, blank=True)
    target_laps = models.PositiveIntegerField(null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(default=50, blank=True)
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'PlanExercise({self.id}) - day {self.day_id} exercise {self.exercise_id}'

    async def get_day(self) -> PlanDay | None:
        return await PlanDay.objects.filter(id=self.day_id).afirst()

    async def get_exercise(self) -> Exercise | None:
        return await Exercise.objects.filter(id=self.exercise_id).afirst()

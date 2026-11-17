from typing import TYPE_CHECKING

from django.db import models

from workout_plan.enums.set_side import SetSide
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.workout_session import WorkoutSession


class SetLog(models.Model):
    """One done set: what was actually lifted, held or covered. Only the fields of the exercise's tracking
    type are filled."""

    if TYPE_CHECKING:
        id: int
        session_id: int
        exercise_id: int
        plan_exercise_id: int | None

    list_display = ['id', 'session', 'exercise', 'set_number', 'side', 'reps', 'weight_kg']
    raw_id_fields = ['session', 'exercise', 'plan_exercise']

    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='set_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='set_logs')
    plan_exercise = models.ForeignKey(
        PlanExercise, on_delete=models.SET_NULL, null=True, blank=True, related_name='set_logs',
    )
    set_number = models.PositiveIntegerField(default=1, blank=True)
    side: SetSide = models.CharField(max_length=8, choices=SetSide.choices(), default=SetSide.BOTH, blank=True)

    reps = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    laps = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['set_number', 'side', 'id']

    def __str__(self) -> str:
        return f'SetLog({self.id}) - session {self.session_id} exercise {self.exercise_id} #{self.set_number}'

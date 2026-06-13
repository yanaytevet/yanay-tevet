from typing import TYPE_CHECKING

from django.db import models

from workout_plan.models.workout_exercise import WorkoutExercise


class ExerciseSet(models.Model):
    if TYPE_CHECKING:
        id: int
        exercise_id: int

    list_display = ['id', 'exercise', 'order', 'reps', 'duration_seconds']
    raw_id_fields = ['exercise']

    exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name='sets')
    order = models.PositiveIntegerField(default=0, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'ExerciseSet({self.id}) - exercise {self.exercise_id}'

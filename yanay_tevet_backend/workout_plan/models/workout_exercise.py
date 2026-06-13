from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from workout_plan.enums.measurement_type import MeasurementType
from workout_plan.models.workout_routine import WorkoutRoutine

if TYPE_CHECKING:
    from workout_plan.models.exercise_set import ExerciseSet


class WorkoutExercise(models.Model):
    if TYPE_CHECKING:
        id: int
        routine_id: int
        sets: Manager['ExerciseSet']

    list_display = ['id', 'routine', 'name', 'measurement_type', 'order']
    list_filter = ['measurement_type']
    raw_id_fields = ['routine']

    routine = models.ForeignKey(WorkoutRoutine, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=255)
    measurement_type: MeasurementType = models.CharField(
        max_length=16,
        choices=MeasurementType.choices(),
        default=MeasurementType.REPS,
        blank=True,
    )
    notes = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'WorkoutExercise({self.id}) - {self.name}'

    async def get_routine(self) -> WorkoutRoutine | None:
        return await WorkoutRoutine.objects.filter(id=self.routine_id).afirst()

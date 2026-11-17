from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from workout_plan.models.workout_plan import WorkoutPlan

if TYPE_CHECKING:
    from workout_plan.models.plan_exercise import PlanExercise


class PlanDay(models.Model):
    """A day type of a plan (Day A, Day B…). The one with is_every_day holds what is done on every day."""

    if TYPE_CHECKING:
        id: int
        plan_id: int
        exercises: Manager['PlanExercise']

    list_display = ['id', 'plan', 'name', 'is_every_day', 'order']
    raw_id_fields = ['plan']

    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='days')
    name = models.CharField(max_length=255, blank=True, default='')
    is_every_day = models.BooleanField(default=False, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['plan'], condition=models.Q(is_every_day=True), name='one_every_day_section_per_plan',
            ),
        ]
        ordering = ['-is_every_day', 'order', 'id']

    def __str__(self) -> str:
        return f'PlanDay({self.id}) - {self.name}'

    async def get_plan(self) -> WorkoutPlan | None:
        return await WorkoutPlan.objects.filter(id=self.plan_id).afirst()

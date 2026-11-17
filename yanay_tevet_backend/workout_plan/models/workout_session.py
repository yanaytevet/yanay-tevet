from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from users.models import User
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.workout_plan import WorkoutPlan

if TYPE_CHECKING:
    from workout_plan.models.set_log import SetLog


class WorkoutSession(models.Model):
    """One workout a user did. Plan and day may later be deleted; the names are kept for the history."""

    if TYPE_CHECKING:
        id: int
        user_id: int
        plan_id: int | None
        day_id: int | None
        set_logs: Manager['SetLog']

    list_display = ['id', 'user', 'plan_name', 'day_name', 'started_at', 'finished_at']
    raw_id_fields = ['user', 'plan', 'day']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    day = models.ForeignKey(PlanDay, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    plan_name = models.CharField(max_length=255, blank=True, default='')
    day_name = models.CharField(max_length=255, blank=True, default='')
    # Copied from the plan when the session starts, so lap counts keep their distance if the plan changes.
    pool_length_m = models.PositiveIntegerField(default=25, blank=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at', '-id']

    def __str__(self) -> str:
        return f'WorkoutSession({self.id}) - {self.day_name} {self.started_at:%Y-%m-%d}'

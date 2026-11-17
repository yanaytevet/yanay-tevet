from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from users.models import User

if TYPE_CHECKING:
    from workout_plan.models.plan_day import PlanDay
    from workout_plan.models.workout_plan_membership import WorkoutPlanMembership


class WorkoutPlan(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        days: Manager['PlanDay']
        memberships: Manager['WorkoutPlanMembership']

    list_display = ['id', 'name', 'owner', 'updated_at']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workout_plans')
    name = models.CharField(max_length=255)
    pool_length_m = models.PositiveIntegerField(default=25, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'WorkoutPlan({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()

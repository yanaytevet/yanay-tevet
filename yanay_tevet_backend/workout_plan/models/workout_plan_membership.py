from typing import TYPE_CHECKING

from django.db import models

from users.models import User
from workout_plan.enums.workout_plan_role import WorkoutPlanRole
from workout_plan.models.workout_plan import WorkoutPlan


class WorkoutPlanMembership(models.Model):
    if TYPE_CHECKING:
        id: int
        plan_id: int
        user_id: int

    list_display = ['id', 'plan', 'user', 'role', 'created_at']
    list_filter = ['role']
    raw_id_fields = ['plan', 'user']

    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plan_memberships')
    role: WorkoutPlanRole = models.CharField(
        max_length=16, choices=WorkoutPlanRole.choices(), default=WorkoutPlanRole.COLLABORATOR, blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['plan', 'user'], name='unique_workout_plan_membership'),
        ]
        ordering = ['id']

    def __str__(self) -> str:
        return f'WorkoutPlanMembership({self.id}) - plan={self.plan_id} user={self.user_id} ({self.role})'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()

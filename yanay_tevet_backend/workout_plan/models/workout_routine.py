from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from users.models import User

if TYPE_CHECKING:
    from workout_plan.models.workout_exercise import WorkoutExercise


class WorkoutRoutine(models.Model):
    if TYPE_CHECKING:
        id: int
        user_id: int
        exercises: Manager['WorkoutExercise']

    list_display = ['id', 'user', 'name', 'order', 'updated_at']
    list_filter = ['user']
    raw_id_fields = ['user']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_routines')
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'WorkoutRoutine({self.id}) - {self.name}'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()

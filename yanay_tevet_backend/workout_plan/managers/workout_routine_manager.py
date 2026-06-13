from django.db.models import Max

from users.models import User
from workout_plan.models.workout_routine import WorkoutRoutine


class WorkoutRoutineManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_routine(self, name: str) -> WorkoutRoutine:
        next_order = await self._next_order()
        routine = WorkoutRoutine(user_id=self.user.id, name=name, order=next_order)
        await routine.asave()
        return routine

    async def _next_order(self) -> int:
        aggregate = await WorkoutRoutine.objects.filter(user_id=self.user.id).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1

from django.db.models import Max

from itinerary_lists.models.itinerary_task import ItineraryTask
from itinerary_lists.serializers.itinerary_task_serializers.itinerary_task_serializer import (
    ItineraryTaskWritableSchema,
)
from common.django_utils.model_utils import ModelUtils
from users.models import User


class ItineraryTaskManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_task(self, itinerary_list_id: int, writable: ItineraryTaskWritableSchema) -> ItineraryTask:
        next_order = await self._next_order(itinerary_list_id)
        task = ItineraryTask(
            itinerary_list_id=itinerary_list_id,
            created_by_id=self.user.id,
            order=next_order,
        )
        await ModelUtils.update_from_schema(task, writable)
        await task.asave()
        return task

    async def update_task(self, task: ItineraryTask, writable: ItineraryTaskWritableSchema) -> None:
        await ModelUtils.update_from_schema(task, writable)
        await task.asave()

    async def _next_order(self, itinerary_list_id: int) -> int:
        aggregate = await ItineraryTask.objects.filter(
            itinerary_list_id=itinerary_list_id
        ).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1

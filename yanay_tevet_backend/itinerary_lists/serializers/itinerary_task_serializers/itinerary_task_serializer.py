from datetime import datetime
from typing import Optional

from ninja import Schema

from itinerary_lists.enums.task_status import TaskStatus
from itinerary_lists.models.itinerary_task import ItineraryTask
from common.simple_api.serializers.serializer import Serializer


class ItineraryTaskSchema(Schema):
    id: int
    itinerary_list_id: int
    name: str
    description: str
    status: TaskStatus
    order: int
    created_at: datetime
    updated_at: datetime


class ItineraryTaskWritableSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    order: Optional[int] = None


class ItineraryTaskSerializer(Serializer[ItineraryTaskSchema]):
    async def inner_serialize(self, obj: ItineraryTask) -> ItineraryTaskSchema:
        return ItineraryTaskSchema(
            id=obj.id,
            itinerary_list_id=obj.itinerary_list_id,
            name=obj.name,
            description=obj.description,
            status=TaskStatus(obj.status),
            order=obj.order,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

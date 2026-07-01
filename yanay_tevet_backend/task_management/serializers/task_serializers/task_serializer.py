from datetime import datetime
from typing import Optional

from ninja import Schema

from task_management.enums.task_priority import TaskPriority
from task_management.enums.task_status import TaskStatus
from task_management.models.task import Task
from common.simple_api.serializers.serializer import Serializer


class TaskSchema(Schema):
    id: int
    project_id: int
    parent_id: Optional[int]
    name: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    due_at: Optional[datetime]
    completed_at: Optional[datetime]
    order: int
    is_repeating: bool
    repeat_days: list[int]
    itinerary_list_id: Optional[int]
    itinerary_list_name: Optional[str]
    subtask_count: int
    done_subtask_count: int
    created_at: datetime
    updated_at: datetime


class TaskWritableSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_at: Optional[datetime] = None
    order: Optional[int] = None
    is_repeating: Optional[bool] = None
    repeat_days: Optional[list[int]] = None
    parent_id: Optional[int] = None
    itinerary_list_id: Optional[int] = None


class TaskSerializer(Serializer[TaskSchema]):
    async def inner_serialize(self, obj: Task) -> TaskSchema:
        itinerary_list = await obj.get_itinerary_list()
        subtask_count = await obj.subtasks.acount()
        done_subtask_count = await obj.subtasks.filter(status=TaskStatus.DONE).acount()
        return TaskSchema(
            id=obj.id,
            project_id=obj.project_id,
            parent_id=obj.parent_id,
            name=obj.name,
            description=obj.description,
            status=TaskStatus(obj.status),
            priority=TaskPriority(obj.priority),
            due_at=obj.due_at,
            completed_at=obj.completed_at,
            order=obj.order,
            is_repeating=obj.is_repeating,
            repeat_days=obj.repeat_days,
            itinerary_list_id=obj.itinerary_list_id,
            itinerary_list_name=itinerary_list.name if itinerary_list else None,
            subtask_count=subtask_count,
            done_subtask_count=done_subtask_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

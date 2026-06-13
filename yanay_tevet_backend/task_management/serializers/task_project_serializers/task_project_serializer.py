from datetime import datetime

from ninja import Schema

from task_management.enums.project_status import ProjectStatus
from task_management.enums.task_status import TaskStatus
from task_management.models.task_project import TaskProject
from common.simple_api.serializers.serializer import Serializer


class TaskProjectSchema(Schema):
    id: int
    name: str
    description: str
    status: ProjectStatus
    owner_id: int
    owner_username: str
    member_count: int
    task_count: int
    open_task_count: int
    created_at: datetime
    updated_at: datetime


class TaskProjectSerializer(Serializer[TaskProjectSchema]):
    async def inner_serialize(self, obj: TaskProject) -> TaskProjectSchema:
        owner = await obj.get_owner()
        member_count = await obj.memberships.acount()
        task_count = await obj.tasks.acount()
        open_task_count = await obj.tasks.exclude(status=TaskStatus.DONE).acount()
        return TaskProjectSchema(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            status=ProjectStatus(obj.status),
            owner_id=obj.owner_id,
            owner_username=owner.username if owner else '',
            member_count=member_count,
            task_count=task_count,
            open_task_count=open_task_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

from datetime import datetime
from typing import Optional

from ninja import Schema
from pydantic import Field

from task_management.enums.task_priority import TaskPriority
from task_management.enums.task_status import TaskStatus
from task_management.serializers.task_project_serializers.task_project_serializer import TaskProjectSchema
from task_management.serializers.task_serializers.task_serializer import TaskSchema

REPEAT_DAYS_DESCRIPTION = (
    'Weekdays a repeating task resets to todo on (at 4 AM in the project owner\'s timezone), '
    'as ints 0=Sunday .. 6=Saturday. Empty means every day. Ignored unless is_repeating.'
)


class NewSubtask(Schema):
    name: str
    description: str = ''
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.NONE
    due_at: Optional[datetime] = Field(default=None, description='ISO 8601 datetime, with timezone.')
    is_repeating: bool = False
    repeat_days: list[int] = Field(default_factory=list, description=REPEAT_DAYS_DESCRIPTION)


class NewTask(NewSubtask):
    parent_id: Optional[int] = Field(
        default=None,
        description='Make this a subtask of an existing top-level task in the same project.',
    )
    subtasks: list[NewSubtask] = Field(
        default_factory=list,
        description='Subtasks to create under this task. Subtasks nest one level only, so this must be '
                    'empty when parent_id is set.',
    )


class TaskChanges(Schema):
    """Only the fields you include are changed."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_at: Optional[datetime] = Field(default=None, description='ISO 8601 datetime; pass null to clear.')
    is_repeating: Optional[bool] = None
    repeat_days: Optional[list[int]] = Field(default=None, description=REPEAT_DAYS_DESCRIPTION)
    parent_id: Optional[int] = Field(
        default=None,
        description='Move under another top-level task in the same project; pass null to make it top-level.',
    )


class TaskProjectDetails(Schema):
    project: TaskProjectSchema
    # Flat, in display order; subtasks carry their parent's id in parent_id.
    tasks: list[TaskSchema]


class DeletedTaskResult(Schema):
    deleted_task_id: int
    deleted_subtask_count: int


class ReorderedTasksResult(Schema):
    project_id: int
    parent_id: Optional[int]
    ordered_task_ids: list[int]

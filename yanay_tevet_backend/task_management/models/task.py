from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from itinerary_lists.models.itinerary_list import ItineraryList
from task_management.enums.task_priority import TaskPriority
from task_management.enums.task_status import TaskStatus
from task_management.models.task_project import TaskProject
from users.models import User

if TYPE_CHECKING:
    from task_management.models.task import Task as TaskRef


class Task(models.Model):
    if TYPE_CHECKING:
        id: int
        project_id: int
        parent_id: int | None
        created_by_id: int | None
        itinerary_list_id: int | None
        subtasks: Manager['TaskRef']

    list_display = ['id', 'name', 'project', 'status', 'priority', 'due_at', 'order', 'updated_at']
    list_filter = ['status', 'priority']
    raw_id_fields = ['project', 'parent', 'created_by', 'itinerary_list']

    project = models.ForeignKey(TaskProject, on_delete=models.CASCADE, related_name='tasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    itinerary_list = models.ForeignKey(
        ItineraryList, on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_tasks'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status: TaskStatus = models.CharField(
        max_length=16,
        choices=TaskStatus.choices(),
        default=TaskStatus.TODO,
        blank=True,
    )
    priority: TaskPriority = models.CharField(
        max_length=16,
        choices=TaskPriority.choices(),
        default=TaskPriority.NONE,
        blank=True,
    )
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f'Task({self.id}) - {self.name}'

    async def get_project(self) -> TaskProject | None:
        return await TaskProject.objects.filter(id=self.project_id).afirst()

    async def get_itinerary_list(self) -> ItineraryList | None:
        if self.itinerary_list_id is None:
            return None
        return await ItineraryList.objects.filter(id=self.itinerary_list_id).afirst()

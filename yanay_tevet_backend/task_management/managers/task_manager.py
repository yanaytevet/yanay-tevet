from django.db.models import Max
from django.utils import timezone

from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from task_management.enums.task_status import TaskStatus
from task_management.models.task import Task
from task_management.serializers.task_serializers.task_serializer import TaskWritableSchema
from common.django_utils.model_utils import ModelUtils
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class TaskManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_task(self, project_id: int, writable: TaskWritableSchema) -> Task:
        await self._validate_parent(project_id, writable.parent_id)
        await self._validate_itinerary_link(writable.itinerary_list_id)
        next_order = await self._next_order(project_id, writable.parent_id)
        task = Task(
            project_id=project_id,
            created_by_id=self.user.id,
            order=next_order,
        )
        await ModelUtils.update_from_schema(task, writable)
        self._sync_completed_at(task)
        await task.asave()
        return task

    async def update_task(self, task: Task, writable: TaskWritableSchema) -> None:
        fields = writable.model_dump(exclude_unset=True)
        if 'parent_id' in fields:
            await self._validate_parent(task.project_id, fields['parent_id'], task_id=task.id)
        if 'itinerary_list_id' in fields:
            await self._validate_itinerary_link(fields['itinerary_list_id'])
        await ModelUtils.update_from_schema(task, writable)
        self._sync_completed_at(task)
        await task.asave()

    def _sync_completed_at(self, task: Task) -> None:
        if task.status == TaskStatus.DONE:
            if task.completed_at is None:
                task.completed_at = timezone.now()
        else:
            task.completed_at = None

    async def _validate_parent(self, project_id: int, parent_id: int | None, task_id: int | None = None) -> None:
        if parent_id is None:
            return
        if parent_id == task_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='A task cannot be its own parent.',
                error_code='invalid_parent',
            )
        parent = await Task.objects.filter(id=parent_id, project_id=project_id).afirst()
        if parent is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='The parent task must belong to the same project.',
                error_code='invalid_parent',
            )
        if parent.parent_id is not None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Subtasks can only be nested one level deep.',
                error_code='invalid_parent',
            )

    async def _validate_itinerary_link(self, itinerary_list_id: int | None) -> None:
        if itinerary_list_id is None:
            return
        itinerary_list = await ItineraryList.objects.filter(id=itinerary_list_id).afirst()
        if itinerary_list is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message='The itinerary list to link was not found.',
                error_code='itinerary_list_not_found',
            )
        is_member = await ItineraryListMembership.objects.filter(
            itinerary_list_id=itinerary_list_id, user_id=self.user.id
        ).aexists()
        if not is_member:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You can only link itinerary lists you are a member of.',
                error_code='itinerary_list_not_accessible',
            )

    async def _next_order(self, project_id: int, parent_id: int | None) -> int:
        aggregate = await Task.objects.filter(
            project_id=project_id, parent_id=parent_id
        ).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1

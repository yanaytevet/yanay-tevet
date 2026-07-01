from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.db.models import Max
from django.utils import timezone

from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from task_management.enums.task_status import TaskStatus
from task_management.models.task import Task
from task_management.models.task_project import TaskProject
from task_management.serializers.task_serializers.task_serializer import TaskWritableSchema
from common.django_utils.model_utils import ModelUtils
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class TaskManager:
    DAILY_RESET_HOUR = 4

    def __init__(self, user: User) -> None:
        self.user = user

    def _tzinfo_from_name(self, timezone_name: str | None) -> ZoneInfo:
        if timezone_name:
            try:
                return ZoneInfo(timezone_name)
            except (ZoneInfoNotFoundError, ValueError):
                pass
        return ZoneInfo('UTC')

    def _last_reset_boundary(self, tzinfo: ZoneInfo, repeat_days: list[int]) -> datetime:
        now = timezone.now().astimezone(tzinfo)
        today_boundary = now.replace(hour=self.DAILY_RESET_HOUR, minute=0, second=0, microsecond=0)
        candidate = today_boundary if now >= today_boundary else today_boundary - timedelta(days=1)
        allowed = self._sanitized_repeat_days(repeat_days)
        if not allowed:
            return candidate
        # Walk back to the most recent 4 AM that falls on one of the task's weekdays.
        for _ in range(7):
            # isoweekday() is 1=Mon..7=Sun; %7 maps it to 0=Sun..6=Sat (JS Date.getDay()).
            if candidate.isoweekday() % 7 in allowed:
                return candidate
            candidate -= timedelta(days=1)
        return candidate

    def _sanitized_repeat_days(self, repeat_days: list[int] | None) -> list[int]:
        if not repeat_days:
            return []
        return sorted({day for day in repeat_days if isinstance(day, int) and 0 <= day <= 6})

    async def reset_due_repeating_tasks(self, project_id: int) -> None:
        project = await TaskProject.objects.select_related('owner').filter(id=project_id).afirst()
        if project is None:
            return
        await self._reset_for_projects([project])

    async def reset_all_due_repeating_tasks(self) -> None:
        projects = [
            project
            async for project in TaskProject.objects.select_related('owner').filter(
                memberships__user_id=self.user.id
            ).distinct()
        ]
        await self._reset_for_projects(projects)

    async def _reset_for_projects(self, projects: list[TaskProject]) -> None:
        now = timezone.now()
        for project in projects:
            tzinfo = self._tzinfo_from_name(project.owner.timezone)
            # Each task may reset on a different set of weekdays, so its due boundary is
            # computed individually rather than with a single project-wide query.
            due_ids = [
                task.id
                async for task in Task.objects.filter(project_id=project.id, is_repeating=True)
                if task.last_reset_at is None
                or task.last_reset_at < self._last_reset_boundary(tzinfo, task.repeat_days)
            ]
            if not due_ids:
                continue
            due_tasks = Task.objects.filter(id__in=due_ids)
            # Reset tasks that were started/completed in a previous cycle back to TODO.
            await due_tasks.exclude(status=TaskStatus.TODO).aupdate(
                status=TaskStatus.TODO,
                completed_at=None,
                last_reset_at=now,
            )
            # Advance the boundary for tasks already in TODO too. Otherwise their
            # last_reset_at stays stale, and they would be wrongly reset the moment
            # they leave TODO later in the same day.
            await due_tasks.filter(status=TaskStatus.TODO).aupdate(last_reset_at=now)

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
        self._sync_repeating(task)
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
        self._sync_repeating(task)
        await task.asave()

    def _sync_repeating(self, task: Task) -> None:
        if task.is_repeating:
            task.repeat_days = self._sanitized_repeat_days(task.repeat_days)
            if task.last_reset_at is None:
                task.last_reset_at = timezone.now()
        else:
            task.repeat_days = []
            task.last_reset_at = None

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

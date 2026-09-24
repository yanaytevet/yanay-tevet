from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from mcp_server.mcp.context import get_current_user
from mcp_server.mcp.schemas.task_schemas import (
    DeletedTaskResult,
    NewTask,
    ReorderedTasksResult,
    TaskChanges,
    TaskProjectDetails,
)
from mcp_server.mcp.tool_errors import handle_tool_errors
from task_management.enums.project_status import ProjectStatus
from task_management.enums.task_status import TaskStatus
from task_management.managers.task_manager import TaskManager
from task_management.managers.task_project_manager import TaskProjectManager
from task_management.models.task import Task
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.permissions_checkers.task_management_permission_checker import TaskManagementPermissionChecker
from task_management.serializers.task_project_serializers.task_project_serializer import (
    TaskProjectSchema,
    TaskProjectSerializer,
)
from task_management.serializers.task_serializers.task_serializer import (
    TaskSchema,
    TaskSerializer,
    TaskWritableSchema,
)
from users.models import User

READ_ONLY = ToolAnnotations(readOnlyHint=True)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True)


async def _get_user() -> User:
    """The connected user, provided they have the Task Management app (the web API applies the same
    check at router level)."""
    user = await get_current_user()
    await TaskManagementPermissionChecker().async_raise_exception_if_not_valid(user)
    return user


async def _load_project(user: User, project_id: int) -> TaskProject:
    project = await TaskProject.objects.filter(id=project_id).afirst()
    if project is None:
        raise ObjectDoesntExistAPIException(TaskProject, project_id)
    await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)
    return project


async def _load_task(user: User, task_id: int) -> Task:
    task = await Task.objects.filter(id=task_id).afirst()
    if task is None:
        raise ObjectDoesntExistAPIException(Task, task_id)
    await _load_project(user, task.project_id)
    return task


def register(mcp: FastMCP) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_task_projects(include_archived: bool = False) -> list[TaskProjectSchema]:
        """List the task projects you're a member of (owned or shared with you), most recently
        updated first, with task counts."""
        user = await _get_user()
        await TaskManager(user).reset_all_due_repeating_tasks()
        projects = TaskProject.objects.filter(memberships__user_id=user.id).distinct().order_by('-updated_at')
        if not include_archived:
            projects = projects.filter(status=ProjectStatus.ACTIVE)
        return await TaskProjectSerializer().serialize_query(projects)

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def get_task_project(project_id: int, include_done: bool = False) -> TaskProjectDetails:
        """Get a project and its tasks (flat, in display order; subtasks carry parent_id). Done tasks
        are left out unless include_done is true."""
        user = await _get_user()
        project = await _load_project(user, project_id)
        await TaskManager(user).reset_due_repeating_tasks(project.id)
        tasks = Task.objects.filter(project_id=project.id).order_by('order', 'id')
        if not include_done:
            tasks = tasks.exclude(status=TaskStatus.DONE)
        return TaskProjectDetails(
            project=await TaskProjectSerializer().serialize(project),
            tasks=await TaskSerializer().serialize_query(tasks),
        )

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def create_task_project(name: str, description: str = '') -> TaskProjectSchema:
        """Create a new task project owned by you."""
        user = await _get_user()
        project = await TaskProjectManager(user).create_project(name, description)
        return await TaskProjectSerializer().serialize(project)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def update_task_project(
        project_id: int,
        name: str | None = None,
        description: str | None = None,
        status: ProjectStatus | None = None,
    ) -> TaskProjectSchema:
        """Rename a project, change its description, or archive/unarchive it (status 'archived' or
        'active'). Omitted fields are left unchanged."""
        user = await _get_user()
        project = await _load_project(user, project_id)
        manager = TaskProjectManager(user)
        await manager.update_project(project, name=name, description=description)
        if status is not None:
            await manager.set_status(project, status)
        return await TaskProjectSerializer().serialize(project)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def create_tasks(project_id: int, tasks: list[NewTask]) -> list[TaskSchema]:
        """Create one or more tasks in a project, each optionally with subtasks. New tasks are added at
        the end of their group. Tasks are created in order; if one fails, the ones before it remain."""
        user = await _get_user()
        project = await _load_project(user, project_id)
        for new_task in tasks:
            if new_task.parent_id is not None and new_task.subtasks:
                raise ValueError(f'"{new_task.name}" has a parent_id, so it cannot have subtasks of its own '
                                 '(subtasks nest one level only).')
        manager = TaskManager(user)
        created: list[Task] = []
        for new_task in tasks:
            task = await manager.create_task(
                project.id, TaskWritableSchema(**new_task.model_dump(exclude={'subtasks'})),
            )
            created.append(task)
            for new_subtask in new_task.subtasks:
                subtask = await manager.create_task(
                    project.id, TaskWritableSchema(**new_subtask.model_dump(), parent_id=task.id),
                )
                created.append(subtask)
        serializer = TaskSerializer()
        return [await serializer.serialize(task) for task in created]

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def update_task(task_id: int, changes: TaskChanges) -> TaskSchema:
        """Update a task — e.g. mark it done (status 'done'), rename it, reprioritize, reschedule or
        move it under another task. Only the fields included in `changes` are modified."""
        user = await _get_user()
        task = await _load_task(user, task_id)
        await TaskManager(user).update_task(task, TaskWritableSchema(**changes.model_dump(exclude_unset=True)))
        return await TaskSerializer().serialize(task)

    @mcp.tool(annotations=DESTRUCTIVE)
    @handle_tool_errors
    async def delete_task(task_id: int) -> DeletedTaskResult:
        """Permanently delete a task. Deleting a task also deletes all of its subtasks. Prefer marking a
        task done unless the user asked for it to be removed."""
        user = await _get_user()
        task = await _load_task(user, task_id)
        subtask_count = await task.subtasks.acount()
        await task.adelete()
        return DeletedTaskResult(deleted_task_id=task_id, deleted_subtask_count=subtask_count)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def reorder_tasks(project_id: int, ordered_task_ids: list[int], parent_id: int | None = None) -> ReorderedTasksResult:
        """Reorder sibling tasks: the top-level tasks of a project (parent_id null) or the subtasks of
        one task (parent_id set). Listed ids go first in the given order; unlisted siblings keep their
        relative order after them."""
        user = await _get_user()
        project = await _load_project(user, project_id)
        await TaskManager(user).reorder_tasks(project.id, parent_id, ordered_task_ids)
        return ReorderedTasksResult(project_id=project.id, parent_id=parent_id, ordered_task_ids=ordered_task_ids)

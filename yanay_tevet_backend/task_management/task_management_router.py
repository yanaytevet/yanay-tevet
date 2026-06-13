from task_management.permissions_checkers.task_management_permission_checker import TaskManagementPermissionChecker
from task_management.views.project_views.create_task_project_view import CreateTaskProjectView
from task_management.views.project_views.delete_task_project_view import DeleteTaskProjectView
from task_management.views.project_views.get_task_project_view import GetTaskProjectView
from task_management.views.project_views.list_task_project_members_view import ListTaskProjectMembersView
from task_management.views.project_views.paginate_task_projects_view import PaginateTaskProjectsView
from task_management.views.project_views.set_task_project_status_view import (
    ArchiveTaskProjectView,
    UnarchiveTaskProjectView,
)
from task_management.views.project_views.share_task_project_view import ShareTaskProjectView
from task_management.views.project_views.unshare_task_project_view import UnshareTaskProjectView
from task_management.views.project_views.update_task_project_view import UpdateTaskProjectView
from task_management.views.task_views.create_task_view import CreateTaskView
from task_management.views.task_views.delete_task_view import DeleteTaskView
from task_management.views.task_views.get_task_view import GetTaskView
from task_management.views.task_views.paginate_tasks_view import PaginateTasksView
from task_management.views.task_views.update_task_view import UpdateTaskView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('task-management', TaskManagementPermissionChecker())

# --- Projects ---
PaginateTaskProjectsView.register_get(router, 'projects/')
CreateTaskProjectView.register_post(router, 'projects/')
GetTaskProjectView.register_get(router, 'projects/{int:object_id}/')
UpdateTaskProjectView.register_patch_by_id(router, prefix='projects')
DeleteTaskProjectView.register_delete_by_id(router, prefix='projects')
ShareTaskProjectView.register_post(router, 'projects/{int:object_id}/share/')
UnshareTaskProjectView.register_post(router, 'projects/{int:object_id}/unshare/')
ListTaskProjectMembersView.register_get(router, 'projects/{int:object_id}/members/')
ArchiveTaskProjectView.register_post(router, 'projects/{int:object_id}/archive/')
UnarchiveTaskProjectView.register_post(router, 'projects/{int:object_id}/unarchive/')

# --- Tasks ---
PaginateTasksView.register_get(router, 'projects/{int:project_id}/tasks/')
CreateTaskView.register_post(router, 'tasks/')
GetTaskView.register_get(router, 'tasks/{int:object_id}/')
UpdateTaskView.register_patch_by_id(router, prefix='tasks')
DeleteTaskView.register_delete_by_id(router, prefix='tasks')

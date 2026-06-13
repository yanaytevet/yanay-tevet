from ninja import Schema

from task_management.enums.project_role import ProjectRole
from task_management.models.task_project_membership import TaskProjectMembership
from common.simple_api.serializers.serializer import Serializer


class ProjectMembershipSchema(Schema):
    id: int
    user_id: int
    username: str
    full_name: str
    role: ProjectRole


class ProjectMembershipSerializer(Serializer[ProjectMembershipSchema]):
    async def inner_serialize(self, obj: TaskProjectMembership) -> ProjectMembershipSchema:
        member = await obj.get_user()
        return ProjectMembershipSchema(
            id=obj.id,
            user_id=obj.user_id,
            username=member.username if member else '',
            full_name=member.get_full_name() if member else '',
            role=ProjectRole(obj.role),
        )

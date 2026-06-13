from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.enums.permissions import Permissions
from users.models import User


class UserPermissionsManager:
    def __init__(self, acting_user: User):
        self.acting_user = acting_user

    async def set_permissions(self, user_id: int, permissions: list[Permissions]) -> User:
        target = await User.objects.filter(id=user_id).afirst()
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message='User not found.',
                error_code='user_not_found',
            )

        is_removing_own_admin = (
            target.id == self.acting_user.id
            and Permissions.ADMIN not in permissions
            and not target.is_superuser
        )
        if is_removing_own_admin:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='You cannot remove your own admin permission.',
                error_code='cannot_remove_own_admin',
            )

        target.permissions = [permission.value for permission in permissions]
        await target.asave(update_fields=['permissions'])
        return target

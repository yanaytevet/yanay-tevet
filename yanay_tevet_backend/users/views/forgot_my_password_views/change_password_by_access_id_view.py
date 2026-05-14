from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.models import TemporaryAccess
from users.serializers.user.user_serializer import UserSerializer, UserSchema


class ChangePasswordByAccessIdSchema(Schema):
    user_id: int
    access_id: str
    new_password: str


class ChangePasswordByAccessIdView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UserSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ChangePasswordByAccessIdSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ChangePasswordByAccessIdSchema, path: Path = None) -> None:
        pass

    @classmethod
    async def run_action(cls, request: APIRequest, data: ChangePasswordByAccessIdSchema, path: Path = None
                         ) -> Schema | None:
        try:
            temporary_access = await TemporaryAccess.objects.filter(
                user_id=data.user_id, access_id=data.access_id).afirst()
        except TemporaryAccess.DoesNotExist as e:
            raise RestAPIException(
                status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                error_code='access_id_is_incorrect',
                message='Access id is incorrect, maybe the link is too old?',
            )

        user = temporary_access.user
        new_pass = str(data.new_password)
        user.set_password(new_pass)
        await user.asave()
        await temporary_access.adelete()

        return await UserSerializer().serialize(temporary_access.user)

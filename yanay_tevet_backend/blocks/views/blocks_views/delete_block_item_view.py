from typing import Type

from django.db.models import Model
from ninja import Schema, Path

from blocks.models import Block
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteBlockItemView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        pass

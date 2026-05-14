from typing import Type

import json
from django.db.models import Model
from ninja import Query, Path

from blocks.models import Block
from blocks.serializers.blocks_serializers.block_serializer import BlockSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.download_files_views.download_file_by_id_view import DownloadFileByIdView
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath


class DownloadBlockByIdView(DownloadFileByIdView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query = None, path: ItemByIdPath = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, query: Query = None, path: ItemByIdPath = None) -> None:
        pass

    @classmethod
    async def get_content_from_object(cls, request: APIRequest, obj: Model, query: Query = None, path: ItemByIdPath = None) -> bytes:
        serialized_block = await BlockSerializer().serialize(obj)
        return json.dumps(serialized_block.dict(), indent=2).encode('utf-8')

    @classmethod
    async def get_content_type(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> str:
        return 'application/json'

    @classmethod
    async def get_file_name(cls, request: APIRequest, query: Query = None, path: Path = None) -> str:
        object_id = path.object_id if path else None
        return f'block_{object_id}.json'
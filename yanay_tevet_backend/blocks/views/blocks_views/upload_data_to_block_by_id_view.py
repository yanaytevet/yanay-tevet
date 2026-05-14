from typing import Type

from django.db.models import Model
from ninja import Schema, UploadedFile

from blocks.enums.block_types import BlockTypes
from blocks.models import Block
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.upload_files_views.upload_files_by_id_view import UploadFilesByIdView


class UploadDataToBlockResponse(Schema):
    total_size: int
    block_type: BlockTypes


class UploadDataToBlockByIdView(UploadFilesByIdView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UploadDataToBlockResponse

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model | None, path) -> None:
        pass

    @classmethod
    async def inner_run_action(cls, api_request: APIRequest, files: list[UploadedFile], obj: Block) -> UploadDataToBlockResponse:
        total_size = sum(file.size for file in files)
        
        return UploadDataToBlockResponse(
            total_size=total_size,
            block_type=obj.block_type
        )
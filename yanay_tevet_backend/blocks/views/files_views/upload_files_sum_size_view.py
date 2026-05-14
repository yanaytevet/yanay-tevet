from typing import Type

from ninja import Schema, Path, UploadedFile

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.upload_files_views.upload_files_view import UploadFilesView


class UploadFilesSumSizeResponse(Schema):
    total_size: int


class UploadFilesSumSizeView(UploadFilesView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UploadFilesSumSizeResponse

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return Schema

    @classmethod
    async def check_permitted(cls, request: APIRequest, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, api_request: APIRequest, files: list[UploadedFile], path: Path = None) -> UploadFilesSumSizeResponse:
        # Calculate the total size of all uploaded files
        total_size = sum(file.size for file in files)
        
        # Return the response with the total size
        return UploadFilesSumSizeResponse(
            total_size=total_size
        )
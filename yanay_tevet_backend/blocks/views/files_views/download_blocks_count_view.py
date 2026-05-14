from ninja import Query, Path

from blocks.models import Block
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.download_files_views.download_file_view import DownloadFileView
from common.xlsx_generator.table_header_schema import TableHeaderSchema
from common.xlsx_generator.xlsx_generator import XlsxGenerator


class DownloadBlocksCountView(DownloadFileView):
    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await api_request.future_user)

    @classmethod
    async def get_content(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> bytes:
        # Count the number of blocks
        blocks_count = await Block.objects.acount()
        
        # Create headers for the xlsx file
        headers = [
            TableHeaderSchema(title="Metric", key="metric"),
            TableHeaderSchema(title="Value", key="value"),
        ]
        
        # Create the xlsx generator
        xlsx_generator = XlsxGenerator(headers)
        
        # Add the blocks count row
        xlsx_generator.add_row({
            "metric": "Number of Blocks",
            "value": blocks_count
        })
        
        # Return the xlsx content
        return xlsx_generator.get_content()

    @classmethod
    async def get_content_type(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> str:
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    @classmethod
    async def get_file_name(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> str:
        return 'blocks_count.xlsx'
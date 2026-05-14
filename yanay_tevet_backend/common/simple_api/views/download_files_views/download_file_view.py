from abc import ABC, abstractmethod
from typing import Type

from django.http import HttpRequest, FileResponse, HttpResponse
from ninja import Router, Query, Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class DownloadFileView(ABC):

    @classmethod
    def register_get(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        query_schema = cls.get_query_params_schema()
        path_schema = cls.get_path_args_schema()
        @router.get(url, tags=cls.get_tags(), operation_id=cls.__name__)
        async def get(request: HttpRequest,
                      query: Query[query_schema] = None,
                      path: Path[path_schema] = None) -> FileResponse:
            api_request = APIRequest(request)
            return await cls().run(api_request, query, path)

    async def run(self, request: APIRequest, query: Query = None, path: Path = None) -> HttpResponse | FileResponse:
        await self.check_permitted(request, query, path)
        return await self.create_file_response(request, query, path)

    async def create_file_response(self, request: APIRequest | None, query: Query = None, path: Path = None) -> HttpResponse | FileResponse:
        content = await self.get_content(request, query, path)
        content_type = await self.get_content_type(request, query, path)
        file_name = await self.get_file_name(request, query, path)
        response = HttpResponse(
            content,
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        response["Content-Length"] = str(len(content))
        return response

    @classmethod
    @abstractmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_content(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> bytes:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_content_type(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_file_name(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> str:
        raise NotImplementedError()

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.__name__]

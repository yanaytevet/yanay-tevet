from abc import ABC, abstractmethod
from typing import Type

from django.http import HttpRequest
from ninja import Router, Schema, Path, File, UploadedFile

from common.simple_api.api_request import APIRequest
from common.urls_utils import UrlsUtils


class UploadFilesView(ABC):

    async def run(self, request: APIRequest, files: list[UploadedFile], path: Path = None) -> Schema:
        await self.check_permitted(request, path)
        return await self.run_action(request, files, path)

    @classmethod
    def register_post(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        resp_schema = cls.get_output_schema()
        path_schema = cls.get_path_args_schema()
        @router.post(url, response=resp_schema, tags=cls.get_tags(), operation_id=cls.__name__)
        async def get(request: HttpRequest,
                      files: list[UploadedFile] = File(...),
                      path: Path[path_schema] = None) -> resp_schema:
            api_request = APIRequest(request)
            return await cls().run(api_request, files, path)

    @classmethod
    @abstractmethod
    async def check_permitted(cls, request: APIRequest, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def run_action(cls, api_request: APIRequest, files: list[UploadedFile], path: Path = None) -> Schema:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_output_schema(cls) -> Type[Schema]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        raise NotImplementedError()

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.__name__]

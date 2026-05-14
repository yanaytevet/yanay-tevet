from abc import ABC, abstractmethod
from typing import Type

from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class SimplePostAPIView(ABC):

    async def run(self, request: APIRequest, data: Schema, path: Path = None) -> Schema:
        await self.check_permitted(request, data, path)
        return await self.run_action(request, data, path)

    @classmethod
    def register_post(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        resp_schema = cls.get_output_schema()
        data_schema = cls.get_data_schema()
        path_schema = cls.get_path_args_schema()
        @router.post(url, response=resp_schema, tags=cls.get_tags(), operation_id=cls.__name__)
        async def post(request: HttpRequest,
                      response: HttpResponse,
                      data: data_schema,
                      path: Path[path_schema] = None) -> resp_schema:
            api_request = APIRequest(request, response=response)
            return await cls().run(api_request, data, path)

    @classmethod
    @abstractmethod
    async def check_permitted(cls, api_request: APIRequest, data: Schema, path: Path = None) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def run_action(cls, api_request: APIRequest, data: Schema, path: Path = None) -> Schema:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_output_schema(cls) -> Type[Schema]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_data_schema(cls) -> Type[Schema]:
        raise NotImplementedError()

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.__name__]

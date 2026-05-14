from abc import ABC, abstractmethod
from typing import Type

from django.http import HttpRequest
from ninja import Router, Query, Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class SimpleGetAPIView(ABC):

    @classmethod
    def register_get(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        resp_schema = cls.get_output_schema()
        query_schema = cls.get_query_params_schema()
        path_schema = cls.get_path_args_schema()
        @router.get(url, response=resp_schema, tags=cls.get_tags(), operation_id=cls.__name__)
        async def get(request: HttpRequest,
                      query: Query[query_schema] = None,
                      path: Path[path_schema] = None) -> resp_schema:
            api_request = APIRequest(request)
            return await cls().run(api_request, query, path)

    async def run(self, request: APIRequest, query: Query = None, path: Path = None) -> Schema:
        await self.check_permitted(request, query, path)
        return await self.get_data(request, query, path)

    @classmethod
    @abstractmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> Schema:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_output_schema(cls) -> Type[Schema]:
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

from abc import ABC, abstractmethod
from typing import Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema, Path, Query

from common.simple_api.views.serialize_item_mixin import SerializeItemMixin
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class ReadItemAPIView(SerializeItemMixin, ABC):
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

    async def run(self, request: APIRequest, query: Query, path: Path) -> Schema:
        await self.check_permitted_before_object(request, query, path)
        obj = await self.get_object(request, None, query, path)
        await self.check_permitted_after_object(request, obj, query, path)
        await self.run_after_get(request, obj, query, path)
        return await self.serialize_object_for_read(request, obj, query, path)

    @classmethod
    @abstractmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_object(cls, request: APIRequest, query: Query, data: Schema, path: Path) -> Model:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, query: Query, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    async def run_after_get(cls, request: APIRequest, obj: Model, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def serialize_object_for_read(cls, request: APIRequest, obj: Model, query: Query, path: Path) -> Schema:
        return await cls.serialize_object(request, obj)

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return cls.get_serializer().get_output_schema()

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.__name__]

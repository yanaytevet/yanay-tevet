from abc import ABC, abstractmethod
from typing import Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema, Path, Query

from common.simple_api.views.serialize_item_mixin import SerializeItemMixin
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class RunActionOnItemAPIView(SerializeItemMixin, ABC):
    @classmethod
    def register_post(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        resp_schema = cls.get_output_schema()
        data_schema = cls.get_data_schema()
        path_schema = cls.get_path_args_schema()
        @router.post(url, response=resp_schema, tags=cls.get_tags(), operation_id=cls.__name__)
        async def post(request: HttpRequest,
                      data: data_schema,
                      path: Path[path_schema] = None) -> resp_schema:
            api_request = APIRequest(request)
            return await cls().run(api_request, data, path)

    async def run(self, request: APIRequest, data: Schema, path: Path) -> Schema:
        await self.check_permitted_before_object(request, data, path)
        obj = await self.get_object(request, None, data, path)
        await self.check_permitted_after_object(request, obj, data, path)
        res = await self.run_action(request, obj, data, path)
        if res is None:
            return await self.serialize_object_after_action(request, obj, data, path)
        else:
            return res

    @classmethod
    @abstractmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def get_object(cls, request: APIRequest, query: Query, data: Schema, path: Path) -> Model:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def run_action(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> Schema | None:
        raise NotImplementedError()

    @classmethod
    async def serialize_object_after_action(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> Schema:
        return await cls.serialize_object(request, obj)

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return cls.get_serializer().get_output_schema()

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

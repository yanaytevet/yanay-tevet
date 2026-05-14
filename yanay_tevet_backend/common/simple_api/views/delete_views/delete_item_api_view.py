from abc import ABC, abstractmethod
from typing import Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema, Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.urls_utils import UrlsUtils


class DeleteItemAPIView(ABC):
    @classmethod
    def register_delete(cls, router: Router, url: str) -> None:
        url = UrlsUtils.fix_url(url)
        data_schema = cls.get_data_schema()
        path_schema = cls.get_path_args_schema()
        @router.delete(url, tags=cls.get_tags(), operation_id=cls.__name__)
        async def delete(request: HttpRequest,
                      data: data_schema = None,
                      path: Path[path_schema] = None) -> EmptySchema:
            api_request = APIRequest(request)
            return await cls().run(api_request, data, path)

    async def run(self, request: APIRequest, data: Schema, path: Path) -> EmptySchema:
        await self.check_permitted_before_object(request, data, path)
        obj = await self.get_object(request, None, data, path)
        await self.check_permitted_after_object(request, obj, data, path)
        await self.run_before_deletion(request, obj, data, path)
        await self.delete_object(request, obj, data, path)
        await self.run_after_deletion(request, obj, data, path)
        return EmptySchema()

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
    async def run_before_deletion(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def delete_object(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        await obj.adelete()

    @classmethod
    async def run_after_deletion(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.__name__]

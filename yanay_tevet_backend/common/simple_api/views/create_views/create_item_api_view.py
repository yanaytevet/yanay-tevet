from abc import ABC, abstractmethod
from typing import Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema, Path

from common.simple_api.views.serialize_item_mixin import SerializeItemMixin
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.django_utils.model_utils import ModelUtils
from common.urls_utils import UrlsUtils


class CreateItemAPIView(SerializeItemMixin, ABC):
    @classmethod
    def register_post(cls, router: Router, url: str = '') -> None:
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
        await self.check_permitted_before_creation(request, data, path)
        await self.run_before_creation(request, data, path)
        obj = await self.create_object(request, data, path)
        await self.run_after_creation(request, obj, data, path)
        return await self.serialize_object_for_creation(request, obj, data, path)

    @classmethod
    @abstractmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    async def run_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def create_object(cls, request: APIRequest, data: Schema, path: Path) -> Model | None:
        model_cls = cls.get_model_cls()
        data = await cls.modify_creation_data(request, data, path)
        return await ModelUtils.create_model_from_schema(model_cls, data)

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: Schema, path: Path) -> Schema:
        return data

    @classmethod
    @abstractmethod
    def get_model_cls(cls) -> Type[Model]:
        raise NotImplementedError()

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def serialize_object_for_creation(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> Schema:
        return await cls.serialize_object(request, obj)

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return cls.get_serializer().get_output_schema()

    @classmethod
    @abstractmethod
    def get_data_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.get_model_cls().__name__]

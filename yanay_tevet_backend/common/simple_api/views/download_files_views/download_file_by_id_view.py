from abc import abstractmethod, ABC
from typing import Type

from django.db.models import Model
from ninja import Query, Path, Schema, Router

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.exceptions.object_id_is_missing_api_exception import ObjectIdIsMissingAPIException
from common.simple_api.views.download_files_views.download_file_view import DownloadFileView
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath


class DownloadFileByIdView(DownloadFileView, ABC):
    @classmethod
    def register_get_by_id(cls, router: Router, suffix: str) -> None:
        cls.register_get(router, f'{{int:object_id}}/{suffix}')

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        await cls.check_permitted_before_object(api_request, query, path)

    @classmethod
    @abstractmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query = None, path: ItemByIdPath = None) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, query: Query = None, path: ItemByIdPath = None) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_model_cls(cls) -> Type[Model]:
        raise NotImplementedError()

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def get_content(cls, api_request: APIRequest, query: Query = None, path: ItemByIdPath = None) -> bytes:
        obj = await cls.get_object(api_request, query, path)
        await cls.check_permitted_after_object(api_request, obj, query, path)
        return await cls.get_content_from_object(api_request, obj, query, path)

    @classmethod
    async def get_object(cls, api_request: APIRequest, query: Query = None, path: ItemByIdPath = None) -> Model | None:
        object_id = path.object_id
        model_cls = cls.get_model_cls()
        if object_id is None:
            raise ObjectIdIsMissingAPIException(model_cls)
        try:
            return await model_cls.objects.aget(id=object_id)
        except model_cls.DoesNotExist as e:
            raise ObjectDoesntExistAPIException(model_cls, object_id)

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.get_model_cls().__name__]

    @classmethod
    @abstractmethod
    async def get_content_from_object(cls, request: APIRequest, obj: Model, query: Query = None, path: ItemByIdPath = None) -> bytes:
        raise NotImplementedError()

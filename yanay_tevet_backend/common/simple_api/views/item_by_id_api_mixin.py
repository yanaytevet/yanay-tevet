from abc import ABC, abstractmethod
from typing import Type, Optional

from django.db.models import Model
from ninja import Path, Schema, Query

from ..api_request import APIRequest
from ..exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from ..exceptions.object_id_is_missing_api_exception import ObjectIdIsMissingAPIException


class ItemByIdPath(Schema):
    object_id: int

class ItemByIdAPIMixin(ABC):
    @classmethod
    async def get_object(cls, request: APIRequest, query: Optional[Query], data: Optional[Query], path: Path[ItemByIdPath]) -> Model:
        object_id = path.object_id
        model_cls = cls.get_model_cls()
        if object_id is None:
            raise ObjectIdIsMissingAPIException(model_cls)
        try:
            return await model_cls.objects.aget(id=object_id)
        except model_cls.DoesNotExist as e:
            raise ObjectDoesntExistAPIException(model_cls, object_id)

    @classmethod
    @abstractmethod
    def get_model_cls(cls) -> Type[Model]:
        raise NotImplementedError()

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    def get_tags(cls) -> list[str]:
        return [cls.get_model_cls().__name__]

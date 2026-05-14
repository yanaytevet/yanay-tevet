from abc import ABC, abstractmethod

from django.db.models import Model, QuerySet
from ninja import Schema

from ..api_request import APIRequest
from ..serializers.serializer import Serializer


class SerializeItemMixin(ABC):
    @classmethod
    async def serialize_object(cls, request: APIRequest, obj: Model) -> Schema:
        return await cls.get_serializer().serialize(obj)

    @classmethod
    async def serialize_query_set(cls, request: APIRequest, query_set: QuerySet) -> list[Schema]:
        return await cls.get_serializer().serialize_query(query_set)

    @classmethod
    @abstractmethod
    def get_serializer(cls) -> Serializer:
        raise NotImplementedError()

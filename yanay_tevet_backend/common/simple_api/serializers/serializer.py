from abc import ABC, abstractmethod
from typing import Type, get_type_hints, Generic, TypeVar

from django.db.models import Model, QuerySet
from ninja import Schema

from users.models import User


T = TypeVar('T', bound=Schema)
class Serializer(ABC, Generic[T]):

    def __init__(self, user: User | None = None):
        self.user = user

    async def serialize(self, obj: Model | None) -> T | None:
        if obj is None:
            return None
        res = await self.inner_serialize(obj)
        if res is not None:
            pass
        return res

    @abstractmethod
    async def inner_serialize(self, obj: Model) -> T | None:
        raise NotImplementedError()

    async def serialize_query(self, cursor: QuerySet) -> list[T]:
        res = [await self.serialize(obj) async for obj in cursor]
        res = [obj for obj in res if obj]
        return res

    @classmethod
    def get_output_schema(cls) -> Type[T]:
        try:
            hints: dict[str, Type[Schema]] = get_type_hints(cls.inner_serialize)
            return_type: Type[T] = hints.get('return', None)
            if return_type is None:
                raise TypeError(f"No return type annotation found for 'inner_serialize' in {cls.__name__}")
            return return_type
        except Exception as e:
            raise TypeError(f"Could not determine return type of 'inner_serialize' in {cls.__name__}: {e}")

from django.db import models
from ninja import Schema
from pydantic import RootModel
from typing import Type, TypeVar, Generic, Any, get_args, get_origin, cast

T = TypeVar("T", bound=Schema)


class SchemaField(models.JSONField, Generic[T]):
    def __init__(self, schema: Type[T] | Type[list[T]], *args: Any, many: bool | None = None, **kwargs: Any) -> None:
        if many is not None:
            self.many: bool = many
            self.schema: Type[T] = cast(Type[T], schema)
        else:
            self.many = get_origin(schema) is list
            if self.many:
                inner = cast(Type[T], get_args(schema)[0])
                self.schema = inner
            else:
                self.schema = cast(Type[T], schema)

        if self.many:
            self._list_schema: Type[RootModel[list[T]]] | None = RootModel[list[self.schema]]  # type: ignore[valid-type]
        else:
            self._list_schema = None

        super().__init__(*args, **kwargs)

    def _deserialize(self, value: Any) -> T | list[T] | None:
        if value is None:
            return None
        if self.many:
            return self._list_schema.model_validate(value).root  # type: ignore[union-attr]
        return self.schema.model_validate(value)

    def _serialize(self, value: Any) -> Any:
        if isinstance(value, list):
            return [i.model_dump() if isinstance(i, Schema) else i for i in value]
        if isinstance(value, Schema):
            return value.model_dump()
        return value

    def _is_already_deserialized(self, value: Any) -> bool:
        if self.many:
            return isinstance(value, list) and all(isinstance(i, self.schema) for i in value)
        return isinstance(value, self.schema)

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> T | list[T] | None:
        parsed = super().from_db_value(value, expression, connection)
        return self._deserialize(parsed)

    def to_python(self, value: Any) -> T | list[T] | None:
        if self._is_already_deserialized(value):
            return value
        parsed = super().to_python(value)
        return self._deserialize(parsed)

    def get_prep_value(self, value: T | list[T] | None) -> Any:
        return super().get_prep_value(self._serialize(value))

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        kwargs["schema"] = self.schema
        kwargs["many"] = self.many
        return name, path, args, kwargs

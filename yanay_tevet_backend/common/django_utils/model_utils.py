import hashlib
from typing import Type

from django.db import models
from django.db.models import Model, Q
from django.forms import model_to_dict
from ninja import Schema

from common.type_hints import JSONType


class ModelUtils:

    @classmethod
    async def update_from_schema(cls, obj: Model, data: Schema) -> None:
        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(obj, key):
                setattr(obj, key, value)

    @classmethod
    async def create_model_from_schema(cls, model_cls: Type[Model], data: Schema) -> Model:
        obj = model_cls()
        await cls.update_from_schema(obj, data)
        await obj.asave()
        return obj

    @classmethod
    def to_json(cls, obj: Model) -> JSONType:
        data = model_to_dict(obj)
        del data['id']
        return data

    @classmethod
    def get_hash_by_fields(cls, obj: Model, fields: list[str]) -> str:
        string = ''.join(getattr(obj, field) for field in fields)
        sha256_hash = hashlib.sha256()
        sha256_hash.update(string.encode('utf-8'))
        return sha256_hash.hexdigest()

    @classmethod
    def exactly_one_not_null_q(cls, *fields: str) -> Q:
        if len(fields) < 2:
            raise ValueError('exactly_one_not_null_q requires at least 2 fields.')

        query = Q()

        for active_field in fields:
            clause = Q(**{f'{active_field}__isnull': False})

            for other_field in fields:
                if other_field != active_field:
                    clause &= Q(**{f'{other_field}__isnull': True})

            query |= clause

        return query

    @classmethod
    def exactly_one_not_null_constraint(
        cls,
        name: str,
        *fields: str,
        violation_error_message: str | None = None,
    ) -> models.CheckConstraint:
        kwargs: dict[str, object] = {
            'name': name,
            'check': cls.exactly_one_not_null_q(*fields),
        }

        if violation_error_message is not None:
            kwargs['violation_error_message'] = violation_error_message

        return models.CheckConstraint(**kwargs)
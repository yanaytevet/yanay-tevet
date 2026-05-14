from django.db.models import Model

from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.serializers.serializer import Serializer


class EmptySerializer(Serializer[EmptySchema]):
    async def inner_serialize(self, obj: Model) -> EmptySchema | None:
        return EmptySchema()

from typing import Type

from django.db.models import Model, QuerySet
from ninja import Query, Path, FilterSchema

from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from dream_diary.serializers.dream_diary_entry_serializers.dream_diary_entry_serializer import DreamDiaryEntrySerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginateDreamDiaryEntriesFilterSchema(FilterSchema):
    pass


class PaginateDreamDiaryEntriesView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return DreamDiaryEntrySerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'time'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateDreamDiaryEntriesFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return DreamDiaryEntry

    @classmethod
    async def apply_initial_filter_and_order(cls, request: APIRequest, queryset: QuerySet,
                                              query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(user=user).order_by('-time')

from abc import ABC

from ninja import Router

from common.simple_api.views.item_by_id_api_mixin import ItemByIdAPIMixin
from common.simple_api.views.read_views.read_item_api_view import ReadItemAPIView


class ReadItemByIdAPIView(ItemByIdAPIMixin, ReadItemAPIView, ABC):
    @classmethod
    def register_get_by_id(cls, router: Router, suffix: str = '') -> None:
        cls.register_get(router, f'{{int:object_id}}/{suffix}')

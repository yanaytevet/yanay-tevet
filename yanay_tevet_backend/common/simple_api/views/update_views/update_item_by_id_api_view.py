from abc import ABC

from ninja import Router

from common.simple_api.views.item_by_id_api_mixin import ItemByIdAPIMixin
from common.simple_api.views.update_views.update_item_api_view import UpdateItemAPIView


class UpdateItemByIdAPIView(ItemByIdAPIMixin, UpdateItemAPIView, ABC):
    @classmethod
    def register_patch_by_id(cls, router: Router, prefix: str = '', suffix: str = '') -> None:
        cls.register_patch(router, f'{prefix}/{{int:object_id}}/{suffix}')

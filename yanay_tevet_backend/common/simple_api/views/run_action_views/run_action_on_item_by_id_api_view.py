from abc import ABC

from ninja import Router

from common.simple_api.views.item_by_id_api_mixin import ItemByIdAPIMixin
from common.simple_api.views.run_action_views.run_action_on_item_api_view import RunActionOnItemAPIView


class RunActionOnItemByIdAPIView(ItemByIdAPIMixin, RunActionOnItemAPIView, ABC):
    @classmethod
    def register_post_by_id(cls, router: Router, suffix: str = '') -> None:
        cls.register_post(router, f'{{int:object_id}}/{suffix}')

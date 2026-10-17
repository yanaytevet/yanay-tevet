from typing import Type

from django.db.models import Model, QuerySet
from django.test import SimpleTestCase
from ninja import FilterSchema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView
from common.simple_api.views.pagination.pagination_input_schemas import PaginationQueryParams
from task_management.models.task_project import TaskProject


class TaskProjectOrderView(PaginateItemsAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return TaskProject

    @classmethod
    def get_serializer(cls):
        raise NotImplementedError()

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        raise NotImplementedError()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'name'}

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: PaginationQueryParams,
                                                path: Path) -> None:
        pass


class OrderByAllowlistTest(SimpleTestCase):
    """The allowlist is what keeps a caller off fields and relations the view never meant to expose,
    so being turned down is an answer they should get — a bare `ValueError` is a 500 and reads as a
    fault on our side."""

    def order_by(self, *items: str) -> QuerySet:
        return TaskProjectOrderView.apply_order_by(
            TaskProject.objects.all(), PaginationQueryParams(order_by=list(items)), None)

    def test_allows_a_listed_field(self) -> None:
        self.assertIsNotNone(self.order_by('name'))

    def test_allows_a_listed_field_in_reverse(self) -> None:
        self.assertIsNotNone(self.order_by('-name'))

    def test_refuses_an_unlisted_field_with_a_client_error(self) -> None:
        with self.assertRaises(RestAPIException) as raised:
            self.order_by('owner__password')
        self.assertEqual(raised.exception.error_code, 'order_by_is_not_allowed')
        self.assertEqual(int(raised.exception.status_code), 400)

    def test_refuses_a_batch_that_contains_one_unlisted_field(self) -> None:
        with self.assertRaises(RestAPIException):
            self.order_by('id', 'created_at')


class DictFilterTest(SimpleTestCase):

    async def test_refuses_a_dict_filter_that_is_not_json_with_a_client_error(self) -> None:
        with self.assertRaises(RestAPIException) as raised:
            await TaskProjectOrderView().generate_query_set(
                None, PaginationQueryParams(dict_filter='{not json'), None)
        self.assertEqual(raised.exception.error_code, 'invalid_dict_filter')
        self.assertEqual(int(raised.exception.status_code), 400)


class PaginationQueryParamsTest(SimpleTestCase):

    def test_caps_the_page_size(self) -> None:
        with self.assertRaises(Exception):
            PaginationQueryParams(page_size=100000)

    def test_refuses_a_negative_page(self) -> None:
        with self.assertRaises(Exception):
            PaginationQueryParams(page=-1)

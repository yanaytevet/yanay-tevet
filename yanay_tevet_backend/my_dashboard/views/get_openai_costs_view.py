from typing import Type

from ninja import Schema, Query, Path as NinjaPath

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from my_dashboard.managers.openai_costs_manager import OpenAICostsManager, OpenAICostsSummary
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker


class OpenAICostsOutput(Schema):
    currency: str
    month_to_date: float
    last_30_days: float
    last_7_days: float
    today: float
    fetched_at: str


class GetOpenAICostsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return OpenAICostsOutput

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> None:
        user = await api_request.future_user
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> OpenAICostsOutput:
        summary: OpenAICostsSummary = await OpenAICostsManager().get_summary()
        return OpenAICostsOutput(**summary.model_dump())

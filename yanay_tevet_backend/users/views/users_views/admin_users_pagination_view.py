from typing import Type, Optional

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView
from common.simple_api.views.pagination.pagination_input_schemas import PaginationQueryParams
from users.models import User
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker
from users.serializers.user.short_user_serializer import ShortUserSerializer


class UserFilterSchema(FilterSchema):
    text: Optional[str] = Field(None, q=[
        'username__icontains', 'email__icontains', 'first_name__icontains', 'last_name__icontains'])


class AdminUsersPaginationView(PaginateItemsAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return User

    @classmethod
    def get_serializer(cls):
        return ShortUserSerializer()

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return UserFilterSchema

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'username', 'email', 'first_name', 'last_name', 'date_joined'}

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: PaginationQueryParams,
                                                path: Path) -> None:
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(await request.future_user)

import datetime
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.enums.special_date_recurrence import SpecialDateRecurrence
from special_dates.models.special_date import SpecialDate
from special_dates.permissions_checkers.own_special_date_permission_checker import OwnSpecialDatePermissionChecker
from special_dates.serializers.special_date_serializers.special_date_serializer import SpecialDateSerializer


class UpdateSpecialDateSchema(Schema):
    date: Optional[datetime.date] = None
    after_sunset: Optional[bool] = None
    category: Optional[SpecialDateCategory] = None
    recurrence: Optional[SpecialDateRecurrence] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)


class UpdateSpecialDateView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateSpecialDateSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SpecialDateSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDate

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SpecialDate, data: Schema, path: Path) -> None:
        await OwnSpecialDatePermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)

from abc import ABC
from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.permissions_checkers.special_date_calendar_member_permission_checker import (
    SpecialDateCalendarMemberPermissionChecker,
)
from special_dates.serializers.special_date_calendar_serializers.special_date_calendar_serializer import (
    SpecialDateCalendarSerializer,
)


class SpecialDateCalendarActionView(RunActionOnItemByIdAPIView, ABC):
    """POST calendars/{id}/<action>/ — checks membership (or ownership) and returns the calendar as the caller sees it."""

    requires_owner = False

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDateCalendar

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SpecialDateCalendarSerializer()

    @classmethod
    async def serialize_object(cls, request: APIRequest, obj: Model) -> Schema:
        return await SpecialDateCalendarSerializer(await request.future_user).serialize(obj)

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: SpecialDateCalendar, data: Schema, path: Path) -> None:
        await SpecialDateCalendarMemberPermissionChecker(obj, require_owner=cls.requires_owner).async_raise_exception_if_not_valid(
            await request.future_user
        )

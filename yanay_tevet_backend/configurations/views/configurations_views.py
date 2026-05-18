from typing import Type

import pytz
from django.conf import settings
from ninja import Schema, Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class FullConfigurationsOutput(Schema):
    timezones: list[str]
    cloudinary_cloud_name: str | None
    google_client_id: str | None


class FullConfigurationsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return FullConfigurationsOutput

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None
                       ) -> FullConfigurationsOutput:
        return FullConfigurationsOutput(
            timezones=list(pytz.all_timezones),
            cloudinary_cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
            google_client_id=settings.GOOGLE_CLIENT_ID,
        )

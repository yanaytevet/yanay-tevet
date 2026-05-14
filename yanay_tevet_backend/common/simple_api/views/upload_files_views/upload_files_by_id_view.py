from abc import ABC, abstractmethod

from django.db.models import Model
from ninja import Router, Schema, Path, UploadedFile

from common.simple_api.api_request import APIRequest
from common.simple_api.views.item_by_id_api_mixin import ItemByIdAPIMixin, ItemByIdPath
from common.simple_api.views.upload_files_views.upload_files_view import UploadFilesView


class UploadFilesByIdView(ItemByIdAPIMixin, UploadFilesView, ABC):
    @classmethod
    def register_post_by_id(cls, router: Router, suffix: str) -> None:
        url = f'{{int:object_id}}/{suffix}'
        cls.register_post(router, url)

    @classmethod
    async def run_action(cls, api_request: APIRequest, files: list[UploadedFile], path: Path[ItemByIdPath] = None) -> Schema:
        obj = await cls.get_object(api_request, None, None, path)
        await cls.check_permitted_after_object(api_request, obj, path)
        return await cls.inner_run_action(api_request, files, obj)

    @classmethod
    @abstractmethod
    async def inner_run_action(cls, api_request: APIRequest, files: list[UploadedFile], obj: Model) -> Schema:
        raise NotImplementedError()

    @classmethod
    async def check_permitted(cls, request: APIRequest, path: Path) -> None:
        await cls.check_permitted_before_object(request, path)

    @classmethod
    @abstractmethod
    async def check_permitted_before_object(cls, request: APIRequest, path: Path) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model | None, path: Path) -> None:
        raise NotImplementedError()

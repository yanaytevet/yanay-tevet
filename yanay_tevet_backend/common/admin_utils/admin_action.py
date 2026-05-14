from typing import Coroutine, Any, Callable, Type

from pydantic import BaseModel

from common.simple_api.views.download_files_views.download_file_by_id_view import DownloadFileByIdView


class AdminAction(BaseModel):
    label: str
    download_file_by_id_view_class: Type[DownloadFileByIdView] | None = None
    callback: Callable[[int], Coroutine[Any, Any, None]] | None = None

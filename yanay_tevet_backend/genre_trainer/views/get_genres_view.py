from typing import Type

from ninja import Schema, Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from genre_trainer.enums.genre_type import GenreType
from genre_trainer.genre_display import GENRE_LABELS


class GetGenresOutput(Schema):
    genres: list[str]
    genre_labels: dict[str, str]


class GetGenresView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return GetGenresOutput

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> GetGenresOutput:
        genres = GenreType.get_list()
        genre_labels = {genre: GENRE_LABELS.get(genre, genre) for genre in genres}
        return GetGenresOutput(genres=genres, genre_labels=genre_labels)

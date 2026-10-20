from typing import Type

from ninja import Schema, Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from genre_trainer.enums.genre_type import GenreType
from genre_trainer.managers.genre_catalog_manager import GenreCatalogManager


class GenreProfileSchema(Schema):
    genre: str
    bpm_min: int
    bpm_max: int
    drums: str
    bass: str
    signature: str
    mood: str
    # The trait that gives the genre away: 'drums', 'bass', 'signature' or 'mood'.
    key_trait: str
    # Rhythm tags compared between genres to find what tells two of them apart; not for display.
    kick_pattern: str
    bass_pattern: str


class GetGenresOutput(Schema):
    genres: list[str]
    profiles: list[GenreProfileSchema]


class GetGenresView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return GetGenresOutput

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> GetGenresOutput:
        return GetGenresOutput(genres=GenreType.get_list(), profiles=GenreCatalogManager.list_profiles())

import json
import random
from pathlib import Path
from typing import Any, Type

from ninja import Schema, Query, Path as NinjaPath

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class GetRandomTrackQuerySchema(Schema):
    genres: str | None = None


class LayerPatternSchema(Schema):
    subdivision: str
    steps: list[str | None]
    velocities: list[float | None] | None = None


class EffectConfigSchema(Schema):
    type: str
    options: dict[str, Any]
    wet: float = 1.0


class InstrumentConfigSchema(Schema):
    type: str
    options: dict[str, Any]


class TrackLayerSchema(Schema):
    id: str
    role: str
    volume: float
    note_duration: str = '16n'
    instrument: InstrumentConfigSchema
    effects: list[EffectConfigSchema]
    pattern: LayerPatternSchema


class TrackSchema(Schema):
    id: str
    genre: str
    bpm: float
    layers: list[TrackLayerSchema]


class GetRandomTrackOutput(Schema):
    track: TrackSchema


TRACKS_DIR = Path(__file__).parent.parent / 'data' / 'tracks'


class GetRandomTrackView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return GetRandomTrackOutput

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return GetRandomTrackQuerySchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> GetRandomTrackOutput:
        genres_filter: set[str] = set()
        if query and query.genres:
            genres_filter = {g for g in query.genres.split(',') if g}

        track_files = list(TRACKS_DIR.glob('*.json'))

        if genres_filter:
            filtered = [f for f in track_files if any(f.name.startswith(g + '_') for g in genres_filter)]
            if filtered:
                track_files = filtered

        track_file = random.choice(track_files)
        with open(track_file) as f:
            track_data = json.load(f)
        return GetRandomTrackOutput(track=TrackSchema.model_validate(track_data))

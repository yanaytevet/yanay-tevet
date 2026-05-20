import random
from typing import Any, Type

from ninja import Schema, Query, Path as NinjaPath

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.genre_generator_registry import GENRE_GENERATORS


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


class AutomationSpecSchema(Schema):
    target: str
    from_val: float
    to_val: float
    waveform: str = 'tri'


class TrackLayerSchema(Schema):
    id: str
    role: str
    volume: float
    note_duration: str = '16n'
    instrument: InstrumentConfigSchema
    effects: list[EffectConfigSchema]
    pattern: LayerPatternSchema
    entry_loop: int = 0
    dropout_prob: float = 0.0
    automation: list[AutomationSpecSchema] = []
    # Optional loop-gating: play only on transport loops where loop_index % loop_modulo == loop_modulo_remainder.
    # 0 means "always play" (default).
    loop_modulo: int = 0
    loop_modulo_remainder: int = 0
    # Stereo position in [-1.0, 1.0]; 0 = center. None lets the player apply a role-based default.
    pan: float | None = None


class TrackSchema(Schema):
    id: str
    genre: str
    bpm: float
    layers: list[TrackLayerSchema]


class GetRandomTrackOutput(Schema):
    track: TrackSchema


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
        available = dict(GENRE_GENERATORS)

        if query and query.genres:
            requested = {g for g in query.genres.split(',') if g}
            filtered = {
                genre_type: gen
                for genre_type, gen in GENRE_GENERATORS.items()
                if genre_type.value in requested
            }
            if filtered:
                available = filtered

        genre_type = random.choice(list(available.keys()))
        generator = available[genre_type]
        track_data = generator.generate()
        return GetRandomTrackOutput(track=TrackSchema.model_validate(track_data))

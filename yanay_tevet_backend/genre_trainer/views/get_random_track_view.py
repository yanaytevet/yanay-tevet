from typing import Any, Type

from ninja import Field, Schema, Query, Path as NinjaPath

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from genre_trainer.managers.genre_catalog_manager import GenreCatalogManager


class GetRandomTrackQuerySchema(Schema):
    genres: str | None = None
    # Pitch class (0 = C … 11 = B) of the key to generate in — the comparison track is made in the key
    # of the track it is played against.
    root: int | None = Field(None, ge=0, le=11)


class LayerPatternSchema(Schema):
    subdivision: str
    steps: list[str | None]
    velocities: list[float | None] | None = None
    # 303-style slide per step: the note glides from the previous one instead of retriggering.
    slides: list[bool] | None = None


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
    # Sidechain duck for this layer ('deep' | 'medium' | 'shallow' | 'none'). None lets the player
    # apply the role-based default.
    sidechain: str | None = None


class TrackSchema(Schema):
    id: str
    genre: str
    bpm: float
    # Transport-level swing applied to 16th notes (0 = straight, ~0.15-0.25 = noticeable shuffle).
    # Per-genre default lives on each generator's SWING class attribute.
    swing: float = 0.0
    # The player ducks everything but the kick on each main-kick hit. Depth scales the duck (0 = off);
    # release is the recovery time in beats.
    sidechain_depth: float = 1.0
    sidechain_release: float = 0.5
    # Per-genre output trim the player applies after its limiter, to level loudness across genres.
    gain_db: float = 0.0
    # The layer role that defines the genre, highlighted on reveal so the listener knows what to solo.
    key_role: str | None = None
    # Pitch class of the track's key (0 = C … 11 = B).
    root: int | None = None
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
        genres = {g for g in query.genres.split(',') if g} if query and query.genres else set()
        track_data = GenreCatalogManager.generate_random_track(genres, query.root if query else None)
        return GetRandomTrackOutput(track=TrackSchema.model_validate(track_data))

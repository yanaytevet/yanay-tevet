import random
import uuid
from typing import Any

from genre_trainer.enums.genre_type import GenreType

_N = None


def _cfg(id_: str, role: str, vol: float, note_dur: str, inst_type: str, inst_opts: dict,
         effects: list, steps: list, velocities: list | None = None) -> dict[str, Any]:
    pattern: dict = {'subdivision': '16n', 'steps': steps}
    if velocities is not None:
        pattern['velocities'] = velocities
    return {
        'id': id_,
        'role': role,
        'volume': vol,
        'note_duration': note_dur,
        'instrument': {'type': inst_type, 'options': inst_opts},
        'effects': effects,
        'pattern': pattern,
    }


def _dist(d: float, wet: float) -> dict:
    return {'type': 'Distortion', 'options': {'distortion': d}, 'wet': wet}


def _reverb(decay: float, wet: float, pre: float | None = None) -> dict:
    opts: dict = {'decay': decay}
    if pre is not None:
        opts['preDelay'] = pre
    return {'type': 'Reverb', 'options': opts, 'wet': wet}


def _delay(t: str, fb: float, wet: float) -> dict:
    return {'type': 'FeedbackDelay', 'options': {'delayTime': t, 'feedback': fb}, 'wet': wet}


def _filt(ftype: str, freq: float, q: float, wet: float = 1.0) -> dict:
    return {'type': 'Filter', 'options': {'type': ftype, 'frequency': freq, 'Q': q}, 'wet': wet}


def _chorus(f: float, dt: float, depth: float, wet: float) -> dict:
    return {'type': 'Chorus', 'options': {'frequency': f, 'delayTime': dt, 'depth': depth}, 'wet': wet}


class BaseTrackGenerator:
    GENRE: GenreType
    BPM_RANGE: tuple[int, int]

    @classmethod
    def generate(cls) -> dict[str, Any]:
        return {
            'id': f'{cls.GENRE.value}_{uuid.uuid4().hex[:6]}',
            'genre': cls.GENRE.value,
            'bpm': random.randint(*cls.BPM_RANGE),
            'layers': cls._generate_layers(),
        }

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    def _pick(cls, pool: list[dict[str, Any]]) -> dict[str, Any]:
        return random.choice(pool)

    @classmethod
    def _maybe(cls, pool: list[dict[str, Any]], probability: float = 0.6) -> dict[str, Any] | None:
        if random.random() < probability:
            return random.choice(pool)
        return None

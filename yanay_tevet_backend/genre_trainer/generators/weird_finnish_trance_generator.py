import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 1.8}},
         [_reverb(1.0, 0.2)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.11, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.65, 'sustain': 0.01, 'release': 2.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.58, 'sustain': 0.01, 'release': 1.7}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_CLAPS = [
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N]),
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.09, 'sustain': 0, 'release': 0.05}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [], [_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

_LEADS = [
    _cfg('lead', 'lead', -8, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(2.5, 0.5, 0.03), _delay('8n.', 0.4, 0.3)],
         ['B4',_N,'D5',_N,'F#5',_N,'G5',_N,'F#5',_N,'E5',_N,'D5',_N,'B4',_N,'B4',_N,'C#5',_N,'D5',_N,'F#5',_N,'A5',_N,'G5',_N,'F#5','E5',_N,_N]),
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(3.0, 0.55, 0.04), _delay('8n.', 0.38, 0.28)],
         ['E5',_N,'G5',_N,'B5',_N,'E6',_N,'B5',_N,'G5',_N,'E5',_N,'D5',_N,'E5',_N,'G5',_N,'B5',_N,'D6',_N,'B5',_N,'G5',_N,'D5',_N,'B4',_N]),
    _cfg('lead', 'lead', -8, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.22, 'release': 0.5}},
         [_reverb(2.8, 0.52, 0.03), _delay('8n.', 0.42, 0.32)],
         ['D5',_N,'F#5',_N,'A5',_N,'D6',_N,'A5',_N,'F#5',_N,'D5',_N,'C#5',_N,'D5',_N,'F#5',_N,'A5',_N,'C#6',_N,'A5',_N,'F#5',_N,'E5',_N,'D5',_N]),
    _cfg('lead', 'lead', -7, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.3, 'sustain': 0.25, 'release': 0.55}},
         [_reverb(3.2, 0.58, 0.04), _delay('8n.', 0.45, 0.35)],
         ['A5',_N,'C#6',_N,'E6',_N,'A6',_N,'E6',_N,'C#6',_N,'A5',_N,'G5',_N,'A5',_N,'C#6',_N,'E6',_N,'G6',_N,'E6',_N,'C#6',_N,'B5',_N,'A5',_N]),
]

_PADS = [
    _cfg('pad', 'pad', -14, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.1, 'decay': 0.5, 'sustain': 0.6, 'release': 1.0}},
         [_reverb(4.0, 0.7)],
         ['B3',_N,_N,_N,_N,_N,_N,_N,'D4',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,'F#3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -16, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.2, 'decay': 0.5, 'sustain': 0.7, 'release': 1.2}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.8, 'release': 1.0}},
         [_reverb(5.0, 0.8)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,'B3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N]),
]


class WeirdFinnishTranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.WEIRD_FINNISH_TRANCE
    BPM_RANGE = (138, 143)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_CLAPS), cls._pick(_LEADS), cls._pick(_PADS)]

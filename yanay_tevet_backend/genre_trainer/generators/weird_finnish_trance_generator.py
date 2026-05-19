import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay, _dist, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 1.8}},
         [_reverb(1.0, 0.2)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.6}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.3}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.11, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.65, 'sustain': 0.01, 'release': 2.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.58, 'sustain': 0.01, 'release': 1.7}},
         [_reverb(0.6, 0.1)], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_CLAPS = [
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.8, 0.3)], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
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
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.2, 'release': 0.4}},
         [_reverb(2.2, 0.45, 0.02), _filt('lowpass', 4000, 2)],
         ['F#5',_N,'A5',_N,'D6',_N,'F#6',_N,'D6',_N,'A5',_N,'F#5',_N,'E5',_N,'F#5',_N,'A5',_N,'C#6',_N,'F#6',_N,'E6',_N,'D6',_N,'C#6',_N,'B5',_N]),
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0.22, 'release': 0.45}},
         [_reverb(3.5, 0.6, 0.05), _delay('4n', 0.35, 0.2)],
         ['B5',_N,_N,'D6','F#6',_N,'B5',_N,'A5',_N,_N,'E5','G5',_N,'F#5',_N,'B5',_N,_N,'D6','G6',_N,'F#6','E6','D6',_N,'C#6',_N,'B5',_N,_N,_N]),
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
    _cfg('pad', 'pad', -15, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.3, 'decay': 0.6, 'sustain': 0.75, 'release': 1.5}},
         [_reverb(5.5, 0.85)],
         ['D3',_N,_N,_N,_N,_N,_N,_N,'F#3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N]),
]

_ARPS = [
    _cfg('arp', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.1, 'release': 0.15}},
         [_reverb(2.0, 0.45), _delay('16n', 0.25, 0.15)],
         ['B4','D5','F#5','B5','D5','F#5','B4','D5','B4','D5','F#5','B5','F#5','D5','B4','D5','B4','D5','G5','B5','D5','G5','B4','D5','A4','E5','A5','E5','A4','E5','A5','E5']),
    _cfg('arp', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.12, 'release': 0.18}},
         [_reverb(2.5, 0.5), _delay('8n', 0.2, 0.12)],
         ['E5','G5','B5','E5','G5','B5','E5','G5','E5','A5','C#6','E5','A5','C#6','E5','A5','D5','F#5','A5','D5','F#5','A5','D5','F#5','E5','G#5','B5','E5','G#5','B5','E5','G#5']),
    _cfg('arp', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.003, 'decay': 0.09, 'sustain': 0.08, 'release': 0.12}},
         [_reverb(1.8, 0.4), _delay('16n', 0.3, 0.18)],
         ['F#5','A5','D6','F#5','A5','D6','F#5','A5','E5','G#5','B5','E5','G#5','B5','E5','G#5','B4','D#5','F#5','B4','D#5','F#5','B4','D#5','A4','C#5','E5','A4','C#5','E5','A4','C#5']),
]


class WeirdFinnishTranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.WEIRD_FINNISH_TRANCE
    BPM_RANGE = (138, 143)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_CLAPS), cls._pick(_LEADS), cls._pick(_PADS)]
        arp = cls._maybe(_ARPS, 0.45)
        if arp:
            layers.append(arp)
        return layers

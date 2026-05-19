import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.2}},
         [], ['C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 2.0}},
         [], ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.8}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.8}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.6}},
         [_reverb(1.0, 0.18)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.5}},
         [_reverb(0.9, 0.15)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01}, 'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 3000, 'octaves': 2.0},
         [], [_N,_N,'C3',_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.03}, 'harmonicity': 3.5, 'modulationIndex': 20, 'resonance': 3500, 'octaves': 1.2},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 350, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.03}, 'harmonicity': 4.0, 'modulationIndex': 24, 'resonance': 4000, 'octaves': 1.2},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.045, 'release': 0.03}, 'harmonicity': 3.8, 'modulationIndex': 22, 'resonance': 3800, 'octaves': 1.2},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.5, 'release': 0.2}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.3, 'release': 0.2, 'baseFrequency': 100, 'octaves': 5}},
         [_dist(0.6, 0.6), _delay('16n', 0.2, 0.1)],
         ['A1','A1',_N,'C2','A1',_N,'G1','A1',_N,'C2','A1',_N,'G1',_N,'A1',_N,'A1','A1',_N,'C2','E2',_N,'D2','C2','A1',_N,'G1','A1','C2',_N,'A1',_N]),
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.03, 'decay': 0.4, 'sustain': 0.8, 'release': 0.4}, 'filterEnvelope': {'attack': 0.03, 'decay': 0.5, 'sustain': 0.7, 'release': 0.4, 'baseFrequency': 60, 'octaves': 1}},
         [], ['A0',_N,_N,_N,_N,_N,_N,_N,'G0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('bass', 'bass', -4, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.7, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.1, 'decay': 0.2, 'sustain': 0.8, 'release': 0.2}},
         [_dist(0.5, 0.5), _filt('lowpass', 800, 6)],
         ['A1',_N,'A1','C2','A1',_N,'G1','A1',_N,'A1',_N,'E1','D1','E1',_N,_N,'A1',_N,'A1','C2','E2',_N,'D2','C2','B1',_N,'A1',_N,'G1','A1',_N,_N]),
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.85, 'release': 0.3}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.8, 'release': 0.3, 'baseFrequency': 55, 'octaves': 1}},
         [], ['D1',_N,_N,_N,'F1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'D1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N]),
    _cfg('bass', 'bass', -6, '16n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 20, 'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.3, 'release': 0.2}},
         [_dist(0.6, 0.6), _reverb(0.4, 0.15, 0.005)],
         ['D2',_N,'D2','F2','D2',_N,'C2','D2','F2','D2',_N,'C2','D2',_N,'A1','C2','D2',_N,'D2','F2','A2','F2','D2','C2','A1','G1','F1',_N,'G1','A1',_N,_N]),
    _cfg('bass', 'bass', -5, '16n', 'FMSynth',
         {'harmonicity': 0.75, 'modulationIndex': 18, 'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.65, 'release': 0.25}, 'modulationEnvelope': {'attack': 0.008, 'decay': 0.1, 'sustain': 0.4, 'release': 0.25}},
         [_dist(0.45, 0.45), _filt('lowpass', 1200, 4)],
         ['G2',_N,'G2','A2','G2','F2','G2',_N,'F2','G2',_N,'E2','D2',_N,'E2','F2','G2',_N,'G2','A2','C3','A2','G2','F2','E2','D2','C2',_N,'D2','E2',_N,_N]),
]


class PsyBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSY_BASS
    BPM_RANGE = (138, 143)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_HIHATS), cls._pick(_BASSES)]

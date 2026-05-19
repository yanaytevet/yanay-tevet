import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.8}},
         [], ['C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.75, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 17, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0.01, 'release': 0.5}},
         [_dist(0.85, 0.65)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 18, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0.01, 'release': 0.5}},
         [_dist(0.9, 0.75)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.016, 'octaves': 20, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0.01, 'release': 0.45}},
         [_dist(0.95, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.7, 0.58)],
         ['C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.78, 0.62)],
         ['C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
]

_PERCS = [
    _cfg('perc', 'perc', -8, '16n', 'MetalSynth',
         {'frequency': 200, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.01}, 'harmonicity': 8.0, 'modulationIndex': 50, 'resonance': 2000, 'octaves': 2.5},
         [_dist(0.9, 0.8)],
         [_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N]),
    _cfg('perc', 'perc', -10, '16n', 'MetalSynth',
         {'frequency': 180, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.015}, 'harmonicity': 7.5, 'modulationIndex': 48, 'resonance': 2500, 'octaves': 2.2},
         [_dist(0.85, 0.75)],
         [_N,_N,'C3',_N,'C3',_N,_N,'C3',_N,_N,_N,'C3','C3',_N,_N,_N,_N,_N,'C3',_N,'C3',_N,_N,'C3',_N,_N,_N,'C3','C3',_N,_N,_N]),
    _cfg('perc', 'perc', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.06}},
         [_dist(0.8, 0.7)],
         ['C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,'C3',_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,'C3',_N,_N,'C3',_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008}, 'harmonicity': 9.0, 'modulationIndex': 60, 'resonance': 7500, 'octaves': 2.0},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.006}, 'harmonicity': 10.0, 'modulationIndex': 65, 'resonance': 8000, 'octaves': 2.2},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 1200, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.008}, 'harmonicity': 12, 'modulationIndex': 80, 'resonance': 12000, 'octaves': 2.8},
         [_dist(0.8, 0.7)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -9, '16n', 'MetalSynth',
         {'frequency': 1400, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.007}, 'harmonicity': 14, 'modulationIndex': 90, 'resonance': 14000, 'octaves': 3.0},
         [_dist(0.85, 0.75)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -11, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.009}, 'harmonicity': 11, 'modulationIndex': 72, 'resonance': 10000, 'octaves': 2.5},
         [_dist(0.75, 0.68)],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4']),
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 950, 'envelope': {'attack': 0.001, 'decay': 0.013, 'release': 0.007}, 'harmonicity': 9.5, 'modulationIndex': 62, 'resonance': 9000, 'octaves': 2.3},
         [], ['C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.1, 'release': 0.05}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.05, 'release': 0.05, 'baseFrequency': 60, 'octaves': 3}},
         [_dist(0.7, 0.7)],
         ['A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N]),
    _cfg('bass', 'bass', -10, '16n', 'MetalSynth',
         {'frequency': 150, 'envelope': {'attack': 0.001, 'decay': 0.08, 'release': 0.04}, 'harmonicity': 1.5, 'modulationIndex': 8, 'resonance': 1500, 'octaves': 0.8},
         [_dist(0.8, 0.7)],
         [_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N,_N,'C3',_N,'C3',_N,_N]),
    _cfg('bass', 'bass', -6, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 5, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.7, 0.6)],
         ['C2',_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N,_N,'C2',_N,_N,'C2','C2',_N,_N,'C2',_N,'C2',_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N]),
    _cfg('bass', 'bass', -5, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 4, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.01, 'release': 0.25}},
         [_dist(0.75, 0.65)],
         ['C2',_N,'C2',_N,_N,'C2',_N,_N,'C2','C2',_N,_N,'C2',_N,'C2',_N,'C2',_N,_N,'C2','C2',_N,_N,_N,'C2','C2',_N,'C2',_N,_N,'C2',_N]),
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.15, 'release': 0.04}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.08, 'release': 0.04, 'baseFrequency': 55, 'octaves': 3.5}},
         [_dist(0.8, 0.72)],
         ['A1','A1',_N,'A1','G1',_N,'A1',_N,'A1',_N,'G1','A1',_N,_N,'A1','A1','A1','A1',_N,'A1','E1',_N,'A1',_N,'G1','A1',_N,'G1','A1',_N,_N,'A1']),
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.12, 'release': 0.05}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.06, 'release': 0.04, 'baseFrequency': 65, 'octaves': 3}},
         [_dist(0.75, 0.68)],
         ['E1','E1',_N,'E1','D1',_N,'E1',_N,'E1',_N,'D1','E1',_N,_N,'E1','E1','E1','E1',_N,'E1','A0',_N,'E1',_N,'D1','E1',_N,'D1','C1',_N,_N,'E1']),
]


class HightekTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HIGHTEK
    BPM_RANGE = (170, 180)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_PERCS), cls._pick(_HIHATS), cls._pick(_BASSES)]

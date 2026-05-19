import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.8}},
         [_dist(0.6, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.75}},
         [_dist(0.7, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.65, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.19, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.8, 0.65)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.72}},
         [_dist(0.65, 0.52)],
         ['C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_PERCS = [
    _cfg('perc', 'perc', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.1}},
         [_dist(0.8, 0.7)],
         [_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3']),
    _cfg('perc', 'perc', -10, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.02}, 'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 4000, 'octaves': 1.5},
         [_dist(0.7, 0.65)],
         [_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,'C3']),
    _cfg('perc', 'perc', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.08}},
         [_dist(0.75, 0.6), _reverb(0.3, 0.15)],
         ['C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 7.0, 'modulationIndex': 50, 'resonance': 6500, 'octaves': 1.8},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01}, 'harmonicity': 8.0, 'modulationIndex': 55, 'resonance': 7000, 'octaves': 2.0},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.016, 'release': 0.01}, 'harmonicity': 7.5, 'modulationIndex': 52, 'resonance': 6800, 'octaves': 1.9},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012}, 'harmonicity': 9.0, 'modulationIndex': 65, 'resonance': 8500, 'octaves': 2.2},
         [_dist(0.5, 0.5)],
         ['C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4']),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015}, 'harmonicity': 8.5, 'modulationIndex': 58, 'resonance': 8000, 'octaves': 2.0},
         [_dist(0.55, 0.5)],
         ['C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4']),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 820, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01}, 'harmonicity': 8.0, 'modulationIndex': 56, 'resonance': 7500, 'octaves': 2.1},
         [_dist(0.45, 0.45)],
         ['C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4',_N,'C4']),
]

_BASSES = [
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.2, 'release': 0.1}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.1, 'release': 0.1, 'baseFrequency': 80, 'octaves': 3}},
         [_dist(0.5, 0.5)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,_N,'G1',_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.04}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.04, 'baseFrequency': 80, 'octaves': 3}},
         [_dist(0.8, 0.7)],
         [_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'E1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N,_N]),
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.1, 'release': 0.06}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.05, 'release': 0.05, 'baseFrequency': 70, 'octaves': 3.5}},
         [_dist(0.65, 0.6)],
         ['A1','A1',_N,'A1',_N,'A1','G1',_N,'A1',_N,'A1',_N,'G1','A1',_N,_N,'A1','A1',_N,'A1',_N,'E1','A1',_N,'G1','A1',_N,'G1','E1',_N,'G1','A1']),
    _cfg('bass', 'bass', -7, '16n', 'MetalSynth',
         {'frequency': 120, 'envelope': {'attack': 0.001, 'decay': 0.1, 'release': 0.05}, 'harmonicity': 1.0, 'modulationIndex': 5, 'resonance': 800, 'octaves': 0.5},
         [_dist(0.75, 0.7)],
         ['C2',_N,'C2',_N,_N,'C2',_N,'C2','C2',_N,_N,'C2',_N,'C2',_N,_N,'C2',_N,'C2',_N,_N,'C2','C2',_N,_N,'C2',_N,'C2',_N,_N,'C2',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 5, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.7, 0.6)],
         ['C2',_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N,_N,'C2',_N,_N,'C2','C2',_N,_N,'C2',_N,'C2',_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N]),
]

_LEADS = [
    _cfg('stab', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.05}},
         [_dist(0.9, 0.6)],
         [_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -16, '16n', 'Synth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.04}},
         [_dist(0.85, 0.55)],
         [_N,_N,_N,_N,_N,_N,'A3',_N,'A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G3',_N,'A3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -14, '16n', 'FMSynth',
         {'harmonicity': 3, 'modulationIndex': 20, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.05}, 'modulationEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.04}},
         [_dist(0.8, 0.6), _reverb(0.3, 0.15)],
         [_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,'G3',_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N]),
]


class TekTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.TEK
    BPM_RANGE = (157, 163)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_PERCS), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]

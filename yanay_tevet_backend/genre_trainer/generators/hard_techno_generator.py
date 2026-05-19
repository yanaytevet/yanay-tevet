import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.1}},
         [_dist(0.4, 0.35)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.45, 0.4)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.033, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.5, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0.01, 'release': 0.95}},
         [_dist(0.48, 0.42)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.55, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.85}},
         [_dist(0.6, 0.48)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_SNARES = [
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.3, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -11, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.055}},
         [_dist(0.5, 0.4)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('snare', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_dist(0.55, 0.42)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01}, 'harmonicity': 5.0, 'modulationIndex': 35, 'resonance': 5000, 'octaves': 1.5},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01}, 'harmonicity': 5.5, 'modulationIndex': 38, 'resonance': 5500, 'octaves': 1.5},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 580, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01}, 'harmonicity': 6.0, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.6},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 620, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01}, 'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 7000, 'octaves': 1.8},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 7.0, 'modulationIndex': 45, 'resonance': 7500, 'octaves': 1.9},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
]

_BASSES = [
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.5, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.3, 'release': 0.2, 'baseFrequency': 120, 'octaves': 2}},
         [_dist(0.5, 0.5)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,'G1',_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,_N,'E1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.4, 'release': 0.15}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.2, 'release': 0.15, 'baseFrequency': 100, 'octaves': 4.5}},
         [_dist(0.6, 0.55)],
         ['E1',_N,'E1','E1','G1',_N,'G1','E1','A1','A1',_N,'G1','E1',_N,'E1',_N,'E1',_N,'E1','E1','F1',_N,'G1','E1','D1','E1',_N,'D1','C1',_N,'D1','E1']),
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.55, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.3, 'release': 0.2, 'baseFrequency': 110, 'octaves': 3}},
         [_dist(0.55, 0.5)],
         ['A1',_N,'A1',_N,'A1','A1','A1',_N,'G1',_N,'G1',_N,'A1','A1',_N,_N,'A1',_N,'A1',_N,'E2','D2','C2',_N,'A1',_N,'G1','A1','E1','F1','G1',_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.38, 'release': 0.18}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.15, 'release': 0.18, 'baseFrequency': 95, 'octaves': 4.2}},
         [_dist(0.58, 0.52)],
         ['D1','D1',_N,'D1','D1','E1','D1',_N,'C1','D1','D1',_N,'D1','D1',_N,'D1','D1','D1',_N,'D1','F1','E1','D1',_N,'C1','B0','A0',_N,'B0','C1','D1',_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.45, 'release': 0.15}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.06, 'sustain': 0.25, 'release': 0.15, 'baseFrequency': 130, 'octaves': 5.0}},
         [_dist(0.5, 0.45), _chorus(3, 3.5, 0.5, 0.2)],
         ['A1',_N,'A1','A1','Bb1',_N,'A1',_N,'G1','A1',_N,'A1','G1',_N,'F1','G1','A1','A1',_N,'Bb1','C2',_N,'Bb1','A1','G1',_N,'F1','G1','A1',_N,_N,'G1']),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.42, 'release': 0.15}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.065, 'sustain': 0.22, 'release': 0.14, 'baseFrequency': 125, 'octaves': 5.2}},
         [_dist(0.55, 0.5)],
         ['E1','E1',_N,'E1','F1',_N,'E1',_N,'D1','E1',_N,'E1','D1',_N,'C#1','D1','E1','E1',_N,'F1','G1',_N,'F1','E1','D1',_N,'C#1','D1','E1',_N,_N,'D1']),
]

_LEADS = [
    _cfg('industrial_stab', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.05}},
         [_dist(0.6, 0.6)],
         [_N,'A3',_N,_N,_N,'A3',_N,'G3',_N,_N,_N,'A3',_N,_N,_N,_N,_N,'A3',_N,_N,_N,'A3',_N,'G3',_N,'E3',_N,_N,'A3',_N,_N,_N]),
    _cfg('industrial_stab', 'lead', -17, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 25, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0.0, 'release': 0.1}, 'modulationEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.1}},
         [_dist(0.7, 0.6)],
         [_N,_N,'A3',_N,_N,'A3',_N,'G3',_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,'A3',_N,'G3','E3',_N,_N,'A3',_N,_N,_N,_N]),
]


class HardTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HARD_TECHNO
    BPM_RANGE = (145, 153)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_SNARES), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]

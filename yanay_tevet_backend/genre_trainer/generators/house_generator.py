import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.6}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.8}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 2.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.58, 'sustain': 0.01, 'release': 1.9}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_CLAPS = [
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.8, 0.4)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0, 'release': 0.09}},
         [_reverb(1.0, 0.45)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.16, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.2, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.004, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.4, 0.52)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0, 'release': 0.12}},
         [_reverb(1.5, 0.45)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.006, 'decay': 0.25, 'sustain': 0, 'release': 0.14}},
         [_reverb(1.8, 0.5)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.08, 'release': 0.06}, 'harmonicity': 3.0, 'modulationIndex': 15, 'resonance': 6000, 'octaves': 1.0},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -11, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.2, 'release': 0.15}, 'harmonicity': 2.5, 'modulationIndex': 12, 'resonance': 7000, 'octaves': 0.8},
         [], [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.04}, 'harmonicity': 2.0, 'modulationIndex': 10, 'resonance': 8000, 'octaves': 0.8},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.07, 'release': 0.05}, 'harmonicity': 2.2, 'modulationIndex': 11, 'resonance': 7500, 'octaves': 0.9},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 440, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012}, 'harmonicity': 4.2, 'modulationIndex': 22, 'resonance': 5500, 'octaves': 1.3},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.5, 'release': 0.3}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.3, 'release': 0.3, 'baseFrequency': 300, 'octaves': 2.5}},
         [], ['G1',_N,'G1',_N,'G1','B1',_N,'G1',_N,_N,'G1',_N,'A1',_N,_N,_N,'G1',_N,'G1',_N,'G1','B1',_N,'G1',_N,_N,'D2',_N,'C2',_N,'B1',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.6, 'release': 0.35}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.35, 'sustain': 0.4, 'release': 0.35, 'baseFrequency': 350, 'octaves': 2}},
         [], ['E1',_N,'E1',_N,'E1','G1',_N,'E1',_N,_N,'E1',_N,'D1',_N,_N,'D1','E1',_N,'E1',_N,'G1','E1',_N,'D1',_N,_N,'B1','A1','G1','E1',_N,_N]),
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.8, 'release': 0.3}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.7, 'release': 0.3, 'baseFrequency': 80, 'octaves': 1.5}},
         [], ['A1',_N,_N,_N,'C2',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'E2',_N,_N,_N,'D2',_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.008, 'decay': 0.22, 'sustain': 0.55, 'release': 0.3}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.32, 'sustain': 0.35, 'release': 0.3, 'baseFrequency': 280, 'octaves': 2.2}},
         [], ['C2',_N,'C2',_N,'C2','Eb2',_N,'C2','Bb1',_N,'C2',_N,'G1','Bb1',_N,_N,'C2',_N,'C2','Eb2','F2','Eb2','C2',_N,'Bb1',_N,'G1','Bb1','C2',_N,'Eb2',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.02, 'decay': 0.35, 'sustain': 0.55, 'release': 0.4}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.45, 'release': 0.35, 'baseFrequency': 200, 'octaves': 2.0}},
         [], ['G1',_N,'G1',_N,_N,'G1',_N,'Bb1','G1',_N,'G1',_N,'F1',_N,_N,'G1','G1',_N,'G1','Bb1',_N,'G1',_N,'F1','Eb1',_N,'F1','G1','Bb1',_N,'G1',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.025, 'decay': 0.38, 'sustain': 0.5, 'release': 0.42}, 'filterEnvelope': {'attack': 0.025, 'decay': 0.42, 'sustain': 0.42, 'release': 0.38, 'baseFrequency': 210, 'octaves': 1.8}},
         [], ['C2',_N,'C2',_N,_N,'C2',_N,'Eb2','C2',_N,'C2',_N,'Bb1',_N,_N,'C2','C2',_N,'C2','Eb2',_N,'C2',_N,'Bb1','Ab1',_N,'Bb1','C2','Eb2',_N,'C2',_N]),
]


class HouseTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HOUSE
    BPM_RANGE = (122, 128)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_CLAPS), cls._pick(_HIHATS), cls._pick(_BASSES)]

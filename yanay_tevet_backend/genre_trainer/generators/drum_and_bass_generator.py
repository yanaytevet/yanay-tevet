import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _filt, _chorus,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.2}},
         [], ['C1',_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 1.1}},
         [], ['C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [], ['C1',_N,_N,'C1',_N,_N,_N,_N,'C1',_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.1}},
         [], ['C1',_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [], ['C1',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1']),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.9}},
         [], ['C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N]),
]

_SNARES = [
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.6, 0.25)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.07}},
         [_reverb(0.8, 0.3)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.7, 0.28)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N]),
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.5, 0.22)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [_reverb(1.0, 0.3)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,'C4',_N]),
    _cfg('snare', 'snare', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [], [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,'C4',_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008}, 'harmonicity': 7.0, 'modulationIndex': 45, 'resonance': 6000, 'octaves': 1.8},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01}, 'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 5500, 'octaves': 1.7},
         [], [_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4']),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.007}, 'harmonicity': 7.5, 'modulationIndex': 48, 'resonance': 6500, 'octaves': 1.9},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
]

_BASSES = [
    _cfg('reese_bass', 'bass', -5, '8n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.7, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.1, 'decay': 0.2, 'sustain': 0.8, 'release': 0.2}},
         [_dist(0.3, 0.4), _filt('lowpass', 900, 3)],
         ['A1',_N,'A1',_N,'G1','A1',_N,_N,'E1','A1',_N,'G1','A1',_N,_N,_N,'A1',_N,'C2','A1','G1',_N,'A1',_N,'E1',_N,'D1','E1','G1','A1',_N,_N]),
    _cfg('reese_bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.6, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.4, 'release': 0.3, 'baseFrequency': 200, 'octaves': 2}},
         [], ['D1',_N,_N,_N,'F1',_N,_N,_N,'D1',_N,_N,_N,'A1',_N,_N,_N,'D1',_N,_N,_N,'G1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N]),
    _cfg('reese_bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.18, 'sustain': 0.55, 'release': 0.28}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.28, 'sustain': 0.35, 'release': 0.28, 'baseFrequency': 180, 'octaves': 2.2}},
         [_chorus(2, 2, 0.4, 0.2)],
         ['F1',_N,'F1','G1','A1',_N,'G1',_N,'F1',_N,'E1',_N,'D1','E1','F1',_N,'F1',_N,'G1',_N,'A1',_N,'C2','A1','G1',_N,'F1',_N,'E1','D1','E1',_N]),
    _cfg('reese_bass', 'bass', -4, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_dist(0.38, 0.45), _filt('lowpass', 1000, 3.5)],
         ['G1',_N,'G1','A1','G1','F1','G1',_N,'E1','G1',_N,'F1','E1',_N,'D1','E1','G1',_N,'G1','A1','C2','A1','G1','F1','E1','D1','C1',_N,'D1','E1','G1',_N]),
    _cfg('reese_bass', 'bass', -4, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_chorus(1.5, 3.5, 0.7, 0.5), _dist(0.3, 0.3)],
         ['D1',_N,'D1','D1',_N,'D1',_N,'D1','C1',_N,'D1',_N,'C1','D1',_N,_N,'D1',_N,'D1','F1','D1',_N,_N,'D1','C1','D1',_N,'C1','Bb0',_N,'C1','D1']),
    _cfg('reese_bass', 'bass', -5, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_chorus(1.2, 3.5, 0.65, 0.48), _dist(0.28, 0.28)],
         ['G1',_N,'G1','G1',_N,'G1',_N,'G1','F1',_N,'G1',_N,'F1','G1',_N,_N,'G1',_N,'G1','Bb1','G1',_N,_N,'G1','F1','G1',_N,'F1','Eb1',_N,'F1','G1']),
]


class DrumAndBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.DRUM_AND_BASS
    BPM_RANGE = (170, 176)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        return [cls._pick(_KICKS), cls._pick(_SNARES), cls._pick(_HIHATS), cls._pick(_BASSES)]

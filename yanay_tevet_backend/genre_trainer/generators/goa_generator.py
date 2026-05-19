import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay, _dist, _chorus,
)

_KICKS = [
    _cfg('kick', 'kick', -3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.7}},
         [_reverb(1.0, 0.14)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.46, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.6}},
         [_reverb(1.5, 0.18)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.062, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.44, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02}, 'harmonicity': 3.5, 'modulationIndex': 18, 'resonance': 7000, 'octaves': 1.0},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.015}, 'harmonicity': 3.0, 'modulationIndex': 16, 'resonance': 6500, 'octaves': 1.0},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02}, 'harmonicity': 3.2, 'modulationIndex': 17, 'resonance': 6000, 'octaves': 1.0},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 720, 'envelope': {'attack': 0.001, 'decay': 0.038, 'release': 0.018}, 'harmonicity': 3.0, 'modulationIndex': 16, 'resonance': 6200, 'octaves': 1.0},
         [], [_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.04}, 'harmonicity': 2.8, 'modulationIndex': 14, 'resonance': 5500, 'octaves': 0.9},
         [], [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.5, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.4, 'release': 0.3, 'baseFrequency': 250, 'octaves': 2.5}},
         [], ['D1',_N,'D1','F1','A1',_N,'G1',_N,'D1',_N,'D1',_N,'A0',_N,'D1',_N,'D1',_N,'D1','F1','A1',_N,'C2',_N,'A1','G1','F1',_N,'D1',_N,'A0',_N]),
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.12, 'sustain': 0.5, 'release': 0.25}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.18, 'sustain': 0.4, 'release': 0.25, 'baseFrequency': 220, 'octaves': 2.5}},
         [], ['D1',_N,'D1',_N,'F1',_N,'D1',_N,'C1',_N,'D1',_N,'A1',_N,'G1',_N,'D1',_N,'D1',_N,'F1',_N,'A1',_N,'G1',_N,'F1',_N,'D1',_N,'C1',_N]),
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.14, 'sustain': 0.48, 'release': 0.28}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.18, 'sustain': 0.38, 'release': 0.28, 'baseFrequency': 230, 'octaves': 2.5}},
         [], ['E1',_N,'E1',_N,'G1',_N,'E1',_N,'D1',_N,'E1',_N,'B1',_N,'A1',_N,'E1',_N,'E1',_N,'G1',_N,'A1',_N,'B1',_N,'A1',_N,'G1',_N,'E1',_N]),
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.45, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.35, 'release': 0.3, 'baseFrequency': 240, 'octaves': 2.5}},
         [], ['G1',_N,'G1',_N,'A1',_N,'G1',_N,'F1',_N,'G1',_N,'D1',_N,'F1',_N,'G1',_N,'G1',_N,'A1',_N,'C2',_N,'A1',_N,'G1',_N,'F1',_N,'G1',_N]),
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.45, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.35, 'release': 0.3, 'baseFrequency': 240, 'octaves': 2.5}},
         [_reverb(1.2, 0.2)],
         ['E1',_N,_N,_N,'E1',_N,'D1',_N,'E1',_N,_N,_N,'D1',_N,'C1',_N,'E1',_N,_N,_N,'E1',_N,'G1',_N,'A1',_N,_N,_N,'G1',_N,'E1',_N]),
    _cfg('bass', 'bass', -9, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.42, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.32, 'release': 0.3, 'baseFrequency': 230, 'octaves': 2.5}},
         [_reverb(1.0, 0.18)],
         ['A1',_N,_N,_N,'A1',_N,'G1',_N,'A1',_N,_N,_N,'G1',_N,'F1',_N,'A1',_N,_N,_N,'A1',_N,'C2',_N,'D2',_N,_N,_N,'C2',_N,'A1',_N]),
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.13, 'sustain': 0.5, 'release': 0.25}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.16, 'sustain': 0.4, 'release': 0.25, 'baseFrequency': 200, 'octaves': 2.8}},
         [], ['B1',_N,'B1',_N,'D2',_N,'B1',_N,'A1',_N,'B1',_N,'G1',_N,'A1',_N,'B1',_N,'B1',_N,'D2',_N,'E2',_N,'D2',_N,'B1',_N,'A1',_N,'G1',_N]),
]

_LEADS = [
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(3.0, 0.5, 0.05), _delay('8n', 0.4, 0.3)],
         ['D5',_N,'F5',_N,'A5',_N,'C6',_N,'A5',_N,'G5',_N,'F5',_N,'D5',_N,'D5',_N,'E5',_N,'F5',_N,'A5',_N,'C6',_N,'A5',_N,'G5',_N,'E5',_N]),
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(2.5, 0.55, 0.02), _delay('8n', 0.3, 0.25)],
         ['D5',_N,_N,'F5',_N,_N,'A5',_N,'G5',_N,_N,_N,'F5',_N,'D5',_N,'D5',_N,_N,'F5',_N,'G5',_N,'A5',_N,'C6',_N,_N,'A5',_N,'G5',_N]),
    _cfg('lead', 'lead', -10, '16n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.5, 'release': 0.5}},
         [_reverb(3.0, 0.6, 0.02), _delay('8n.', 0.3, 0.25)],
         ['E5',_N,_N,_N,'G5',_N,'B5',_N,'A5',_N,'G5',_N,'E5',_N,_N,_N,'E5',_N,_N,_N,'A5',_N,'B5',_N,'D6',_N,_N,_N,'B5',_N,'A5',_N]),
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(3.0, 0.6, 0.02), _delay('8n.', 0.32, 0.22)],
         ['G5',_N,_N,'A5',_N,'C6',_N,_N,'A5',_N,'G5',_N,'F5',_N,_N,_N,'G5',_N,_N,'A5','C6',_N,'D6',_N,'C6','A5',_N,_N,'G5',_N,_N,_N]),
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.22, 'release': 0.5}},
         [_reverb(4.0, 0.7, 0.04), _delay('8n.', 0.45, 0.35)],
         ['E5','G5','B5','E6','B5','G5','E5','D5','E5','G5','B5','D6','B5','G5','D5','C5','E5','G5','B5','E6','G6','E6','B5','G5','A5','C6','E6','A6','E6','C6','A5','G5']),
    _cfg('lead', 'lead', -9, '16n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.25, 'release': 0.5}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.5, 'release': 0.5}},
         [_reverb(5.0, 0.72, 0.05), _delay('8n.', 0.5, 0.38)],
         ['A5','C6','E6','A6','E6','C6','A5','G5','A5','C6','E6','G6','E6','C6','G5','F5','A5','C6','E6','A6','B6','A6','E6','C6','D6','F6','A6','D7','A6','F6','D6','C6']),
    _cfg('lead', 'lead', -10, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 6, 'envelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.2, 'release': 0.48}, 'modulationEnvelope': {'attack': 0.4, 'decay': 0.15, 'sustain': 0.4, 'release': 0.4}},
         [_reverb(3.5, 0.65, 0.03), _delay('8n', 0.35, 0.28)],
         ['B5',_N,'D6',_N,'E6',_N,'G6',_N,'E6',_N,'D6',_N,'B5',_N,'A5',_N,'B5',_N,'D6',_N,'E6',_N,'F#6',_N,'E6',_N,'D6','B5',_N,_N,'A5',_N]),
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.24, 'sustain': 0.2, 'release': 0.46}},
         [_reverb(3.2, 0.58, 0.03), _delay('8n.', 0.38, 0.3)],
         ['A5',_N,'C6',_N,'E6',_N,'A6',_N,'G6',_N,'E6',_N,'C6',_N,'A5',_N,'A5',_N,'B5','C6','E6',_N,'G6',_N,'E6','C6','A5',_N,'G5','A5','C6',_N,_N,_N]),
]

_ARPS = [
    _cfg('arp', 'lead', -15, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0.1, 'release': 0.2}},
         [_reverb(2.5, 0.5), _delay('16n', 0.3, 0.2)],
         ['D6','F6','A6','D7','A6','F6','D6','C6','D6','F6','A6','C7','A6','F6','C6','Bb5','D6','F6','A6','D7','F7','D7','A6','F6','E6','G6','B6','E7','B6','G6','E6','D6']),
    _cfg('arp', 'lead', -16, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.08, 'release': 0.18}, 'modulationEnvelope': {'attack': 0.4, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_reverb(3.0, 0.55), _delay('16n', 0.28, 0.22)],
         ['E6','G6','B6','E7','B6','G6','E6','D6','E6','G6','B6','D7','B6','G6','D6','C6','E6','G6','B6','E7','G7','E7','B6','G6','A6','C7','E7','A7','E7','C7','A6','G6']),
    _cfg('arp', 'lead', -17, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.003, 'decay': 0.2, 'sustain': 0.12, 'release': 0.25}},
         [_reverb(4.0, 0.6), _delay('8n', 0.4, 0.3)],
         ['A5',_N,'C6',_N,'E6',_N,'A6',_N,'E6',_N,'C6',_N,'A5',_N,'G5',_N,'B5',_N,'D6',_N,'G6',_N,'D6',_N,'B5',_N,'G5',_N,'F5',_N]),
]


class GoaTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.GOA
    BPM_RANGE = (136, 142)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]
        arp = cls._maybe(_ARPS, 0.5)
        if arp:
            layers.append(arp)
        return layers

import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.1, 0.15)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.7}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 2.0}},
         [_reverb(1.2, 0.15)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.3}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.12, 0.2)],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01}, 'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 4000, 'octaves': 1.5},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01}, 'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 5000, 'octaves': 1.2},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008}, 'harmonicity': 4.8, 'modulationIndex': 28, 'resonance': 4500, 'octaves': 1.3},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 450, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.012}, 'harmonicity': 5.2, 'modulationIndex': 33, 'resonance': 4300, 'octaves': 1.4},
         [], [_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.18, 'release': 0.12}, 'harmonicity': 4.8, 'modulationIndex': 28, 'resonance': 4200, 'octaves': 1.4},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01}, 'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 4600, 'octaves': 1.4},
         [], ['C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 420, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01}, 'harmonicity': 5.3, 'modulationIndex': 34, 'resonance': 4400, 'octaves': 1.5},
         [], ['C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.6, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.5, 'release': 0.3, 'baseFrequency': 200, 'octaves': 3}},
         [_dist(0.3, 0.4)],
         ['A1',_N,'A1',_N,'C2',_N,'A1',_N,'G1',_N,'A1',_N,'E1',_N,'A1',_N,'A1',_N,'A1',_N,'C2',_N,'E2',_N,'D2',_N,'C2',_N,'A1',_N,'G1',_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.5, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.4, 'release': 0.2, 'baseFrequency': 150, 'octaves': 4}},
         [_dist(0.25, 0.35)],
         ['E1',_N,'E1','G1','A1',_N,'A1',_N,'G1',_N,'E1',_N,'D1','E1',_N,_N,'E1',_N,'E1','G1','A1',_N,'C2',_N,'B1',_N,'A1',_N,'G1','E1',_N,_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.12, 'sustain': 0.55, 'release': 0.25}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.45, 'release': 0.25, 'baseFrequency': 180, 'octaves': 3.5}},
         [_dist(0.35, 0.45)],
         ['A1',_N,_N,_N,'G1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N,'A1',_N,_N,_N,'C2',_N,_N,_N,'D2',_N,_N,_N,'E2',_N,_N,_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.5, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.07, 'sustain': 0.3, 'release': 0.2, 'baseFrequency': 160, 'octaves': 4.5}},
         [_dist(0.3, 0.4)],
         ['D1',_N,'D1',_N,'F1','D1',_N,'D1','C1',_N,'D1',_N,'A1','G1',_N,_N,'D1',_N,'D1','F1','A1',_N,'G1','F1','D1','C1',_N,'D1','E1','F1',_N,_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.4, 'release': 0.18}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.25, 'release': 0.18, 'baseFrequency': 140, 'octaves': 4.8}},
         [_dist(0.35, 0.4)],
         ['A1',_N,'A1','C2','D2',_N,'C2','A1','G1','A1',_N,'G1','E1','G1',_N,_N,'A1',_N,'C2','D2','E2','D2','C2','A1','G1',_N,'F1','G1','A1',_N,_N,_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.45, 'release': 0.18}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.075, 'sustain': 0.28, 'release': 0.18, 'baseFrequency': 150, 'octaves': 4.6}},
         [_dist(0.38, 0.42)],
         ['G1',_N,'G1','Bb1','C2',_N,'Bb1','G1','F1','G1',_N,'F1','D1','F1',_N,_N,'G1',_N,'Bb1','C2','D2','C2','Bb1','G1','F1','D1',_N,'F1','G1',_N,_N,'F1']),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.11, 'sustain': 0.5, 'release': 0.22}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.14, 'sustain': 0.4, 'release': 0.22, 'baseFrequency': 170, 'octaves': 3.8}},
         [_dist(0.28, 0.38)],
         ['A1',_N,_N,'Bb1',_N,'A1',_N,'G1','F1',_N,'A1',_N,'G1',_N,'F1',_N,'A1',_N,_N,'C2',_N,'A1',_N,'G1','F1','A1',_N,'G1','Bb1',_N,'A1',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.55, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.4, 'release': 0.2, 'baseFrequency': 130, 'octaves': 4.2}},
         [_dist(0.3, 0.38)],
         ['E1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,'G1','E1',_N,_N,_N,'E1',_N,'G1',_N,'A1',_N,'B1',_N,'C2',_N,'B1','A1','G1','E1',_N,_N]),
]

_LEADS = [
    _cfg('lead', 'lead', -12, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(1.2, 0.35, 0.01), _delay('16n', 0.25, 0.15)],
         ['A4',_N,_N,'C5',_N,_N,'E5',_N,'D5',_N,_N,_N,'C5',_N,'A4',_N,'A4',_N,_N,'C5',_N,_N,'G5',_N,'E5',_N,_N,_N,'C5',_N,'A4',_N]),
    _cfg('lead', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.15, 'release': 0.4}},
         [_reverb(1.5, 0.3, 0.01), _delay('16n', 0.2, 0.12)],
         ['E5',_N,_N,'G5',_N,_N,'A5',_N,'G5',_N,_N,_N,'E5',_N,_N,_N,'D5',_N,_N,'E5',_N,_N,'G5',_N,'A5',_N,_N,_N,'B5',_N,'A5',_N]),
    _cfg('lead', 'lead', -13, '16n', 'FMSynth',
         {'harmonicity': 3, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5}, 'modulationEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.3, 'release': 0.5}},
         [_reverb(1.2, 0.28, 0.01), _delay('8n', 0.18, 0.1)],
         ['A4',_N,_N,_N,'C5',_N,'E5',_N,'D5',_N,'C5',_N,_N,_N,'A4',_N,'G4',_N,_N,_N,'A4',_N,'C5',_N,'E5',_N,'G5',_N,'E5',_N,'D5',_N]),
    _cfg('lead', 'lead', -13, '16n', 'AMSynth',
         {'harmonicity': 2, 'envelope': {'attack': 0.008, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.8, 'release': 0.4}},
         [_reverb(1.3, 0.32, 0.01), _delay('16n', 0.22, 0.12)],
         ['D5',_N,_N,'F5',_N,'A5',_N,_N,'G5',_N,_N,'F5','D5',_N,_N,_N,'D5',_N,'E5','F5','A5',_N,_N,'G5','F5','E5',_N,_N,'D5',_N,_N,_N]),
    _cfg('lead', 'lead', -11, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 12, 'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.15, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.3, 'decay': 0.1, 'sustain': 0.6, 'release': 0.3}},
         [_reverb(1.5, 0.35, 0.02), _delay('16n', 0.18, 0.14)],
         ['A4',_N,_N,'C5',_N,'E5',_N,'D5','C5',_N,_N,'A4',_N,_N,'G4',_N,'A4',_N,'C5','E5',_N,'G5','F5','E5','D5','C5',_N,_N,'A4',_N,_N,_N]),
    _cfg('lead', 'lead', -11, '16n', 'FMSynth',
         {'harmonicity': 2.0, 'modulationIndex': 14, 'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.12, 'release': 0.38}, 'modulationEnvelope': {'attack': 0.4, 'decay': 0.12, 'sustain': 0.5, 'release': 0.3}},
         [_reverb(1.6, 0.38, 0.02), _delay('16n', 0.2, 0.12)],
         ['G5',_N,_N,'Bb5',_N,'D6',_N,'C6','Bb5',_N,_N,'G5',_N,_N,'F5',_N,'G5',_N,'Bb5','D6',_N,'F6','Eb6','D6','C6','Bb5',_N,_N,'G5',_N,_N,_N]),
    _cfg('lead', 'lead', -12, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(1.4, 0.32, 0.01), _delay('16n', 0.22, 0.13)],
         ['A4','C5',_N,'E5','D5',_N,'C5',_N,'A4',_N,'G4',_N,'A4','C5',_N,_N,'E5',_N,'G5',_N,'E5','D5','C5',_N,'A4',_N,'G4','A4','C5',_N,_N,_N]),
    _cfg('lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 2.5, 'modulationIndex': 10, 'envelope': {'attack': 0.008, 'decay': 0.26, 'sustain': 0.14, 'release': 0.42}, 'modulationEnvelope': {'attack': 0.35, 'decay': 0.1, 'sustain': 0.55, 'release': 0.32}},
         [_reverb(1.8, 0.4, 0.02), _delay('8n', 0.2, 0.1)],
         ['E5',_N,'F5',_N,'G5',_N,'A5',_N,'G5',_N,'F5',_N,'E5',_N,_N,_N,'E5',_N,'G5',_N,'A5',_N,'B5',_N,'A5',_N,'G5','F5','E5',_N,_N,_N]),
]

_PADS = [
    _cfg('pad', 'pad', -16, '16n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.8, 'release': 1.5}},
         [_reverb(4.0, 0.7)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -18, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.9, 'release': 2.5}},
         [_reverb(5.0, 0.8), _chorus(0.5, 3, 0.4, 0.3)],
         ['E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -17, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.4, 'decay': 0.6, 'sustain': 0.75, 'release': 2.2}, 'modulationEnvelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.7, 'release': 2.0}},
         [_reverb(4.5, 0.75)],
         ['D2',_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -20, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.9, 'release': 3.0}},
         [_reverb(6.0, 0.85)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
]


class PsytranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSYTRANCE
    BPM_RANGE = (145, 150)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]
        pad = cls._maybe(_PADS, 0.45)
        if pad:
            layers.append(pad)
        return layers

import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.6, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.75, 0.65)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.7, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.024, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.8}},
         [_dist(0.65, 0.58)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 17, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0.01, 'release': 0.55}},
         [_dist(0.8, 0.7)],
         ['C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.19, 'sustain': 0.01, 'release': 0.62}},
         [_dist(0.72, 0.62)],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.026, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.55, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_SNARES = [
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_dist(0.5, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_dist(0.55, 0.52)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_dist(0.5, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_reverb(0.6, 0.25)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -6, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.006}, 'harmonicity': 8.5, 'modulationIndex': 55, 'resonance': 7000, 'octaves': 2.0},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.005}, 'harmonicity': 9.5, 'modulationIndex': 60, 'resonance': 8000, 'octaves': 2.2},
         [], ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4']),
    _cfg('hihat', 'hihat', -6, '16n', 'MetalSynth',
         {'frequency': 1100, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.007}, 'harmonicity': 11, 'modulationIndex': 70, 'resonance': 10000, 'octaves': 2.5},
         [_dist(0.3, 0.3)], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.008}, 'harmonicity': 8.0, 'modulationIndex': 52, 'resonance': 6500, 'octaves': 1.9},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.011, 'release': 0.006}, 'harmonicity': 9.0, 'modulationIndex': 58, 'resonance': 7500, 'octaves': 2.1},
         [_dist(0.25, 0.25)], ['C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4']),
]

_ACID_BASSES = [
    # Classic A minor acid line
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.05}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.05, 'baseFrequency': 80, 'octaves': 4.5}},
         [_dist(0.5, 0.5)],
         ['A2','A2',_N,'A2','A2','A2',_N,'A2',_N,'A2','A2',_N,'C3','C3',_N,'A2','A2','A2',_N,'A2','A2',_N,'A2',_N,'G2','G2','A2',_N,'E2',_N,'G2',_N]),
    # E minor acid with octave jumps
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.04}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.04, 'baseFrequency': 90, 'octaves': 5.0}},
         [_dist(0.55, 0.55)],
         ['E2','E3',_N,'E2','E2','E3',_N,'E2',_N,'G2','E3','E2','B2',_N,'E2',_N,'E2','E3',_N,'E2','E2',_N,'D2','D3','E2',_N,'B1',_N,'D2','E2',_N,_N]),
    # D acid with chromatic passing tones
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.0, 'release': 0.05}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.05, 'baseFrequency': 75, 'octaves': 4.8}},
         [_dist(0.6, 0.58)],
         ['D2',_N,'D2','Eb2','D2',_N,'C2','D2','D2',_N,'E2','D2',_N,'C#2','D2',_N,'D2',_N,'F2','E2','D2',_N,'C2',_N,'D2','Eb2','E2',_N,'F2',_N,'E2','D2']),
    # Rapid-fire A accent pattern
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.03}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 85, 'octaves': 5.5}},
         [_dist(0.65, 0.6)],
         ['A2','A2','A2',_N,'A2','A2',_N,'A2','A2',_N,'A2','A2',_N,'A2','A2',_N,'A2','A2','A2',_N,'C3','C3',_N,'A2','A2',_N,'A2','G2','A2',_N,'E2','A2',_N]),
    # G acid line with open filter
    _cfg('bass', 'bass', -3, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.05, 'release': 0.06}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.02, 'release': 0.06, 'baseFrequency': 100, 'octaves': 4.2}},
         [_dist(0.45, 0.45)],
         ['G2',_N,'G2','A2','G2',_N,'F2','G2',_N,'G2','A2','G2','F2',_N,'G2',_N,'G2',_N,'G2','Bb2','A2',_N,'G2',_N,'F2','G2',_N,'E2','F2','G2',_N,_N]),
    # B acid with tight envelope
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0.0, 'release': 0.025}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0.0, 'release': 0.025, 'baseFrequency': 70, 'octaves': 6.0}},
         [_dist(0.7, 0.65)],
         ['B1','B2','B1',_N,'B1','B2',_N,'B1','B1',_N,'B2','B1',_N,'B2','B1',_N,'B1','B2','B1',_N,'A1','B1',_N,'G#1','B1',_N,'A1',_N,'B1','A1',_N,_N]),
]

_LEADS = [
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.2, 'release': 0.3}},
         [_dist(0.4, 0.4), _reverb(0.8, 0.3)],
         ['A4',_N,_N,'C5','A4',_N,'E4',_N,'G4',_N,_N,'A4',_N,'G4','A4',_N,'A4',_N,_N,'C5','E5',_N,'D5','C5','A4',_N,'G4',_N,'A4',_N,_N,_N]),
    _cfg('lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 2.5, 'modulationIndex': 6, 'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.25, 'release': 0.3}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.1, 'release': 0.25}},
         [_dist(0.35, 0.35), _reverb(1.0, 0.35)],
         ['E4',_N,'G4',_N,'A4',_N,'B4','A4',_N,'G4','E4',_N,_N,'G4',_N,_N,'E4',_N,'G4',_N,'A4',_N,'C5','A4',_N,'G4',_N,'E4',_N,_N,_N]),
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0.22, 'release': 0.35}},
         [_dist(0.3, 0.3), _delay('8n', 0.2, 0.12)],
         ['D5','D5',_N,'F5','A5','F5','D5',_N,'C5','D5',_N,'A4','C5',_N,'D5',_N,'D5',_N,'F5','A5','C6','A5','F5',_N,'E5','D5',_N,'C5','D5',_N,_N,_N]),
]


class AcidTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.ACID_TECHNO
    BPM_RANGE = (133, 140)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_SNARES), cls._pick(_HIHATS), cls._pick(_ACID_BASSES)]
        lead = cls._maybe(_LEADS, 0.4)
        if lead:
            layers.append(lead)
        return layers

import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.2, 0.3)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.3, 0.4)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.7, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.036, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.25}},
         [_dist(0.75, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.4}},
         [_dist(0.25, 0.35)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.2, 0.3)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.85, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01}, 'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.5},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01}, 'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.5},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01}},
         [_dist(0.6, 0.55)],
         [_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4']),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01}, 'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.5},
         [], ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008}},
         [_dist(0.7, 0.6)],
         [_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 350, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 5000, 'octaves': 1.4},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,_N]),
]

_BASSES = [
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 30, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.2, 'release': 0.1}},
         [_dist(0.7, 0.5), _filt('lowpass', 600, 4)],
         ['A1',_N,'A1','Bb1','A1',_N,'G1','A1','F1','A1',_N,'G1','Eb1',_N,'F1','G1','A1',_N,'A1','Bb1','C2','Bb1','A1','G1','F1',_N,'Eb1',_N,'F1','G1',_N,_N]),
    _cfg('dark_bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.55, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.3, 'release': 0.2, 'baseFrequency': 150, 'octaves': 4}},
         [_dist(0.8, 0.55), _filt('lowpass', 700, 8)],
         ['E1',_N,'E1','F1','E1','D1','E1',_N,'C1',_N,'E1','D1','C1','B0',_N,'C1','E1',_N,'E1','F1','G1','F1','E1','D1','C1','B0','A0',_N,'B0','C1',_N,_N]),
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 30, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.2, 'release': 0.1}},
         [_dist(0.9, 0.6), _filt('bandpass', 500, 5, 0.7)],
         ['D1',_N,'D1','F1','D1','C1','D1','Eb1','F1','D1','C1','Bb0','A0',_N,'Bb0','C1','D1',_N,'D1','F1','G1','Ab1','G1','F1','Eb1','D1','C1','Bb0','C1','D1',_N,_N]),
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 28, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.2, 'release': 0.1}},
         [_dist(0.75, 0.52), _filt('lowpass', 650, 5)],
         ['C1',_N,'C1','Db1','C1','B0','C1',_N,'Ab0',_N,'C1','B0','Ab0',_N,'B0','C1','C1',_N,'C1','Db1','Eb1','Db1','C1','B0','Ab0',_N,'G0',_N,'Ab0','B0',_N,_N]),
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 32, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.2, 'release': 0.1}},
         [_dist(0.9, 0.65), _reverb(0.6, 0.12)],
         ['C1','C1',_N,'C1',_N,'C1','Db1',_N,'C1',_N,'C1',_N,'Bb0',_N,'C1','C1','C1',_N,'C1','Eb1',_N,'C1',_N,'C1','Db1','C1',_N,_N,'C1',_N,'Bb0',_N]),
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 35, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.2, 'release': 0.1}},
         [_dist(0.95, 0.7), _reverb(0.5, 0.1)],
         ['Bb0','Bb0',_N,'Bb0',_N,'Bb0','B0',_N,'Bb0',_N,'Bb0',_N,'Ab0',_N,'Bb0','Bb0','Bb0',_N,'Bb0','Db1',_N,'Bb0',_N,'Bb0','B0','Bb0',_N,_N,'Ab0',_N,'G0',_N]),
    _cfg('dark_bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.2}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.25, 'release': 0.2, 'baseFrequency': 120, 'octaves': 5}},
         [_dist(0.85, 0.6), _filt('lowpass', 550, 6)],
         ['G0',_N,'G0','Ab0','G0','F0',_N,'G0','Eb0','F0','G0',_N,'Ab0','G0',_N,'F0','G0',_N,'G0','Bb0','G0','Ab0',_N,'G0','F0',_N,'Eb0','F0','G0',_N,_N,_N]),
]

_LEADS = [
    _cfg('alien_lead', 'lead', -15, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 15, 'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_reverb(1.5, 0.35, 0.01), _dist(0.3, 0.3)],
         ['A4',_N,_N,'Bb4',_N,_N,'G4',_N,'Eb4',_N,_N,_N,'F4',_N,'G4',_N,'A4',_N,_N,'Bb4',_N,'C5',_N,'Bb4','A4',_N,'G4',_N,'Eb4',_N,_N,_N]),
    _cfg('alien_lead', 'lead', -19, '16n', 'AMSynth',
         {'harmonicity': 0.25, 'envelope': {'attack': 0.005, 'decay': 0.5, 'sustain': 0.1, 'release': 0.5}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(4.0, 0.7, 0.05), _dist(0.4, 0.4)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('alien_lead', 'lead', -14, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 15, 'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_reverb(2.0, 0.4, 0.01), _dist(0.5, 0.4)],
         ['D4',_N,_N,'Eb4',_N,_N,'F4',_N,'Eb4',_N,_N,_N,'D4',_N,_N,_N,'Bb3',_N,_N,'C4',_N,_N,'D4',_N,'F4',_N,'Eb4',_N,'D4',_N,'C4',_N]),
    _cfg('alien_lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 18, 'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_dist(0.6, 0.5), _reverb(2.0, 0.4)],
         ['C4',_N,_N,'Eb4',_N,_N,'Db4',_N,'C4',_N,'Bb3',_N,_N,'Ab3',_N,'C4','C4',_N,'Eb4','Gb4',_N,'Eb4',_N,'Db4','C4',_N,_N,_N,'Bb3','Ab3',_N,_N]),
    _cfg('alien_lead', 'lead', -13, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 18, 'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_dist(0.65, 0.55), _reverb(2.5, 0.45)],
         ['Bb3',_N,_N,'Db4',_N,_N,'B3',_N,'Bb3',_N,'Ab3',_N,_N,'G3',_N,'Bb3','Bb3',_N,'Db4','Eb4',_N,'Db4',_N,'B3','Bb3',_N,_N,_N,'Ab3','G3',_N,_N]),
    _cfg('alien_lead', 'lead', -16, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 15, 'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_reverb(1.8, 0.38, 0.01), _dist(0.35, 0.32)],
         ['C4',_N,_N,'Db4',_N,'Eb4',_N,_N,'Db4',_N,_N,_N,'C4',_N,'Ab3',_N,'C4',_N,_N,'Db4',_N,'Eb4','F4','Eb4','Db4',_N,'C4',_N,'Ab3',_N,_N,_N]),
    _cfg('alien_lead', 'lead', -14, '16n', 'AMSynth',
         {'harmonicity': 0.3, 'envelope': {'attack': 0.005, 'decay': 0.4, 'sustain': 0.08, 'release': 0.45}, 'modulationEnvelope': {'attack': 0.4, 'decay': 0.2, 'sustain': 0.15, 'release': 0.4}},
         [_dist(0.5, 0.45), _reverb(2.2, 0.42)],
         ['G3',_N,'Ab3',_N,'Bb3',_N,'G3',_N,'F3',_N,'G3',_N,'Eb3',_N,_N,_N,'G3',_N,'Ab3','Bb3','Db4','Bb3','Ab3','G3','F3',_N,'Eb3',_N,'F3','G3',_N,_N,_N]),
]

_TEXTURES = [
    _cfg('texture', 'pad', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.3, 'release': 2.0}},
         [_reverb(6.0, 0.9), _dist(0.2, 0.3)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('texture', 'pad', -24, '16n', 'AMSynth',
         {'harmonicity': 0.1, 'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.6, 'release': 3.0}, 'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.5, 'release': 2.0}},
         [_reverb(8.0, 0.95), _dist(0.3, 0.25)],
         ['Ab1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
]


class DarkPsyTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.DARK_PSY
    BPM_RANGE = (148, 150)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]
        texture = cls._maybe(_TEXTURES, 0.35)
        if texture:
            layers.append(texture)
        return layers

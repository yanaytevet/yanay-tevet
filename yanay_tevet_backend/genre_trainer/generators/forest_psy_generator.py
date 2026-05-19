import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.4, 0.4)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.45, 0.42)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1','C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.5, 0.48)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.4}},
         [_dist(0.38, 0.38), _reverb(0.5, 0.1)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.1}},
         [_dist(0.52, 0.5)],
         ['C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.44, 'sustain': 0.01, 'release': 1.25}},
         [_dist(0.42, 0.42)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.46, 'sustain': 0.01, 'release': 1.35}},
         [_dist(0.6, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.025}},
         [_filt('highpass', 3000, 1)],
         [_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.028, 'sustain': 0, 'release': 0.018}},
         [_filt('highpass', 4000, 1)],
         [_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N,_N,'C3',_N,_N,_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 250, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02}, 'harmonicity': 5.5, 'modulationIndex': 38, 'resonance': 2500, 'octaves': 1.8},
         [_dist(0.3, 0.3)],
         [_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N]),
    _cfg('hihat', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.035}},
         [_filt('highpass', 2500, 1)],
         [_N,_N,'C3','C3',_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3','C3',_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.022, 'sustain': 0, 'release': 0.015}},
         [_filt('highpass', 5000, 1)],
         ['C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N]),
]

_BASSES = [
    # Dark A Phrygian chromatic bass
    _cfg('bass', 'bass', -4, '16n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 25, 'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0.55, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.3, 'release': 0.2}},
         [_dist(0.65, 0.6), _filt('lowpass', 900, 3)],
         ['A1',_N,'A1','Bb1','A1',_N,'G1','A1','Bb1','A1',_N,'G1','A1',_N,'F1','G1','A1',_N,'A1','Bb1','C2','Bb1','A1',_N,'G1','A1','Bb1',_N,'A1',_N,_N,'G1']),
    # B Locrian dark movement
    _cfg('bass', 'bass', -5, '16n', 'FMSynth',
         {'harmonicity': 0.4, 'modulationIndex': 30, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.5, 'release': 0.18}, 'modulationEnvelope': {'attack': 0.002, 'decay': 0.07, 'sustain': 0.25, 'release': 0.18}},
         [_dist(0.7, 0.65), _reverb(0.3, 0.1, 0.002)],
         ['B1',_N,'B1','C2','B1',_N,'A1','B1','C2','B1',_N,'A1','Bb1',_N,'A1','B1','B1',_N,'C2','B1','D2','C2','B1',_N,'A1','Bb1','B1',_N,'A1',_N,_N,'G1']),
    # E Phrygian alien bass
    _cfg('bass', 'bass', -4, '16n', 'AMSynth',
         {'harmonicity': 0.3, 'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0.6, 'release': 0.22}, 'modulationEnvelope': {'attack': 0.05, 'decay': 0.12, 'sustain': 0.5, 'release': 0.2}},
         [_dist(0.6, 0.58), _filt('lowpass', 700, 4)],
         ['E2',_N,'E2','F2','E2',_N,'D2','E2','F2','E2',_N,'D2','E2',_N,'C2','D2','E2',_N,'E2','F2','G2','F2','E2','D2','C2',_N,'D2','E2','F2',_N,'E2',_N]),
    # D minor heavy sub
    _cfg('bass', 'bass', -3, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.6, 'release': 0.2}, 'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.35, 'release': 0.18, 'baseFrequency': 70, 'octaves': 4.5}},
         [_dist(0.55, 0.52)],
         ['D1',_N,_N,_N,'D1',_N,'D1',_N,'D1',_N,_N,_N,'C1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,'Eb1',_N,'D1',_N,'C1',_N,'D1',_N,_N,_N]),
    # C chromatic descent
    _cfg('bass', 'bass', -5, '16n', 'FMSynth',
         {'harmonicity': 0.6, 'modulationIndex': 22, 'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.52, 'release': 0.2}, 'modulationEnvelope': {'attack': 0.003, 'decay': 0.09, 'sustain': 0.28, 'release': 0.18}},
         [_dist(0.62, 0.58), _filt('lowpass', 1000, 3)],
         ['C2',_N,'C2','C#2','C2',_N,'B1','C2','C#2','C2',_N,'B1','Bb1','B1','C2',_N,'C2',_N,'C#2','D2','C2',_N,'B1',_N,'C2','C#2','D2','C#2','C2','B1',_N,_N]),
    # G dark phrygian syncopated
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.45, 'release': 0.15}, 'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.2, 'release': 0.12, 'baseFrequency': 75, 'octaves': 4}},
         [_dist(0.68, 0.62)],
         ['G1','G1',_N,'Ab1','G1',_N,'F1','G1','G1',_N,'Ab1','G1','F1',_N,'G1',_N,'G1',_N,'G1','Ab1','Bb1','Ab1','G1',_N,'F1','G1','Ab1',_N,'G1','F1',_N,_N]),
]

_LEADS = [
    _cfg('lead', 'lead', -10, '16n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 18, 'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.3, 'release': 0.4}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.15, 'release': 0.35}},
         [_dist(0.5, 0.5), _reverb(1.8, 0.5, 0.01)],
         ['A4',_N,'Bb4',_N,'A4',_N,'G4',_N,'F4',_N,'A4',_N,'C5',_N,'Bb4',_N,'A4',_N,'G4',_N,'F4','G4','A4',_N,'E4',_N,'F4',_N,'A4',_N,'G4',_N]),
    _cfg('lead', 'lead', -11, '16n', 'FMSynth',
         {'harmonicity': 4.0, 'modulationIndex': 22, 'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.25, 'release': 0.38}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.12, 'release': 0.3}},
         [_dist(0.6, 0.58), _reverb(2.2, 0.55, 0.015)],
         ['E5',_N,_N,'F5','E5',_N,'D5','E5',_N,'F5','E5',_N,'D5',_N,'C5','D5','E5',_N,_N,'F5','G5','F5','E5',_N,'D5','E5','F5',_N,'E5',_N,_N,'D5']),
    _cfg('lead', 'lead', -10, '16n', 'AMSynth',
         {'harmonicity': 2.0, 'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.3, 'release': 0.45}, 'modulationEnvelope': {'attack': 0.01, 'decay': 0.12, 'sustain': 0.2, 'release': 0.4}},
         [_dist(0.45, 0.45), _reverb(2.5, 0.58, 0.02), _delay('16n', 0.2, 0.12)],
         ['B4',_N,'C5',_N,'B4',_N,'A4',_N,'G4','A4','B4',_N,'C5',_N,'B4',_N,'B4','A4',_N,'G4','A4','B4',_N,'D5','C5','B4',_N,'A4',_N,'G4',_N,_N,_N]),
    _cfg('lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 5.0, 'modulationIndex': 28, 'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.2, 'release': 0.35}, 'modulationEnvelope': {'attack': 0.003, 'decay': 0.06, 'sustain': 0.1, 'release': 0.28}},
         [_dist(0.7, 0.65), _reverb(3.0, 0.65, 0.02)],
         ['D5',_N,'Eb5','D5',_N,'C5',_N,'D5','Eb5',_N,'D5','C5','Bb4',_N,'C5','D5','D5',_N,'Eb5',_N,'F5','Eb5','D5',_N,'C5','D5',_N,'C5','Bb4','C5','D5',_N,_N]),
]

_TEXTURES = [
    _cfg('texture', 'pad', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.5, 'decay': 1.0, 'sustain': 0.8, 'release': 2.0}},
         [_reverb(6.0, 0.9), _filt('bandpass', 800, 4)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('texture', 'pad', -20, '16n', 'AMSynth',
         {'harmonicity': 0.1, 'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.85, 'release': 2.5}, 'modulationEnvelope': {'attack': 1.0, 'decay': 0.3, 'sustain': 0.9, 'release': 2.0}},
         [_reverb(7.0, 0.92), _filt('lowpass', 600, 2)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('texture', 'pad', -19, '16n', 'FMSynth',
         {'harmonicity': 0.2, 'modulationIndex': 5, 'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.8, 'release': 2.2}, 'modulationEnvelope': {'attack': 0.8, 'decay': 0.3, 'sustain': 0.85, 'release': 2.0}},
         [_reverb(6.5, 0.9), _filt('lowpass', 500, 2)],
         ['E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
]


class ForestPsyTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.FOREST_PSY
    BPM_RANGE = (148, 155)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        layers = [cls._pick(_KICKS), cls._pick(_HIHATS), cls._pick(_BASSES), cls._pick(_LEADS)]
        texture = cls._maybe(_TEXTURES, 0.4)
        if texture:
            layers.append(texture)
        return layers

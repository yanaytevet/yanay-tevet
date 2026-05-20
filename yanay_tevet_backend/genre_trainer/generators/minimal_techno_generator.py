import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _auto,
    _vel, _vel_groove, _vel_kick,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.8}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.95}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.31, 'sustain': 0.01, 'release': 0.92}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.1}},
         [_reverb(0.4, 0.08)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0.01, 'release': 0.75}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 7.0, 'modulationIndex': 40, 'resonance': 5000, 'octaves': 1.8},
         [],
         [_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008}, 'harmonicity': 8.0, 'modulationIndex': 45, 'resonance': 6000, 'octaves': 2.0},
         [],
         [_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N]),
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.012}, 'harmonicity': 7.5, 'modulationIndex': 42, 'resonance': 5500, 'octaves': 1.9},
         [],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.007}, 'harmonicity': 9.0, 'modulationIndex': 50, 'resonance': 7000, 'octaves': 2.1},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.014}, 'harmonicity': 6.5, 'modulationIndex': 38, 'resonance': 4500, 'octaves': 1.7},
         [],
         [_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
]

_BASSES = [
    # Monotone deep A loop
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.7, 'release': 0.4}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.65, 'release': 0.4, 'baseFrequency': 55, 'octaves': 0.8}},
         [],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N]),
    # Two-note D/A minimal groove
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.015, 'decay': 0.25, 'sustain': 0.75, 'release': 0.35}, 'filterEnvelope': {'attack': 0.015, 'decay': 0.35, 'sustain': 0.7, 'release': 0.35, 'baseFrequency': 50, 'octaves': 1.0}},
         [],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'A0',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'A0',_N,_N,_N]),
    # Slightly syncopated G
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.025, 'decay': 0.35, 'sustain': 0.72, 'release': 0.42}, 'filterEnvelope': {'attack': 0.025, 'decay': 0.45, 'sustain': 0.68, 'release': 0.4, 'baseFrequency': 52, 'octaves': 0.9}},
         [],
         ['G0',_N,_N,_N,'G0',_N,_N,'G0',_N,_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,_N,_N,_N,_N,'G0',_N,_N,_N]),
    # E deep pulse
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.018, 'decay': 0.28, 'sustain': 0.68, 'release': 0.38}, 'filterEnvelope': {'attack': 0.018, 'decay': 0.38, 'sustain': 0.62, 'release': 0.36, 'baseFrequency': 48, 'octaves': 1.0}},
         [],
         ['E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'B0',_N,_N,_N,'E1',_N,_N,_N]),
    # Slow A/G movement
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.03, 'decay': 0.4, 'sustain': 0.78, 'release': 0.5}, 'filterEnvelope': {'attack': 0.03, 'decay': 0.5, 'sustain': 0.72, 'release': 0.45, 'baseFrequency': 58, 'octaves': 0.7}},
         [],
         ['A0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N,'G0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N]),
    # Subtle sawtooth with filter
    _cfg('bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.6, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.18, 'sustain': 0.35, 'release': 0.28, 'baseFrequency': 60, 'octaves': 2.5}},
         [_filt('lowpass', 400, 3)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_STABS = [
    _cfg('stab', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.0, 'release': 0.06}},
         [_reverb(1.2, 0.4), _filt('lowpass', 2500, 2)],
         [_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.06, 'sustain': 0.0, 'release': 0.05}},
         [_reverb(1.5, 0.45), _filt('lowpass', 2000, 2)],
         [_N,_N,_N,_N,'D4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'D4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -15, '16n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.0, 'release': 0.08}, 'modulationEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.0, 'release': 0.06}},
         [_reverb(1.8, 0.5)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N]),
]


class MinimalTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.MINIMAL_TECHNO
    BPM_RANGE = (124, 132)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.15, ghost_prob=0.1)

        # Minimal breathes: hi-hat may dropout for whole bars to create space
        if random.random() < 0.5:
            hihat['dropout_prob'] = random.choice([0.25, 0.35, 0.45])

        layers = [kick, hihat, bass]

        if random.random() < 0.5:
            stab = copy.deepcopy(cls._pick(_STABS))
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
            # Stab enters late — Villalobos-style sparse arrangement
            stab['entry_loop'] = random.choice([2, 4])
            layers.append(stab)

        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus, _filt, _delay, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

# ---------------------------------------------------------------------------
# KICKS — distorted, hammering, the centrepiece. All include distortion.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.1}},
         [_dist(0.4, 0.35)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.45, 0.4)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.033, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.5, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.55, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.85}},
         [_dist(0.6, 0.48)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Pumping double on beat 4 — Berlin/Cleric style
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.42, 0.38)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    # Maximum crunch — Sara Landry energy
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.75}},
         [_dist(0.7, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# SNARES / CLAPS — punching backbeat at 2 & 4.
# ---------------------------------------------------------------------------
_SNARES = [
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.3, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # High-pitch distorted clap
    _cfg('snare', 'snare', -11, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.055}},
         [_dist(0.5, 0.4)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('snare', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_dist(0.55, 0.42)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    # With ghost roll into beat 4
    _cfg('snare', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — driving 16ths, often with distortion for the gritty top end.
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01},
          'harmonicity': 5.0, 'modulationIndex': 35, 'resonance': 5000, 'octaves': 1.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01},
          'harmonicity': 5.5, 'modulationIndex': 38, 'resonance': 5500, 'octaves': 1.5},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 580, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.6},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 620, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 7000, 'octaves': 1.8},
         [],
         ['C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,
          'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N]),
    # Distorted 16ths — peak-time energy
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.012},
          'harmonicity': 5.8, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.7},
         [_dist(0.3, 0.25)],
         ['C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4',
          'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4']),
]

# ---------------------------------------------------------------------------
# BASSES — distorted saw growls with chromatic motion.
# Some have filter automation for evolving brightness.
# ---------------------------------------------------------------------------
_BASSES = [
    # A minor sustained
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.5, 'release': 0.2},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.3, 'release': 0.2,
                             'baseFrequency': 120, 'octaves': 2}},
         [_dist(0.5, 0.5)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,'G1',_N,_N,_N,_N,_N,_N,_N,
          'A1',_N,_N,_N,_N,_N,_N,_N,'E1',_N,_N,_N,_N,_N,_N,_N]),
    # E rolling minor
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.4, 'release': 0.15},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.2, 'release': 0.15,
                             'baseFrequency': 100, 'octaves': 4.5}},
         [_dist(0.6, 0.55)],
         ['E1',_N,'E1','E1','G1',_N,'G1','E1','A1','A1',_N,'G1','E1',_N,'E1',_N,
          'E1',_N,'E1','E1','F1',_N,'G1','E1','D1','E1',_N,'D1','C1',_N,'D1','E1'],
         automation=[_auto('effect:0:wet', 0.4, 0.7, 'tri')]),
    # A minor melodic
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.55, 'release': 0.2},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.3, 'release': 0.2,
                             'baseFrequency': 110, 'octaves': 3}},
         [_dist(0.55, 0.5)],
         ['A1',_N,'A1',_N,'A1','A1','A1',_N,'G1',_N,'G1',_N,'A1','A1',_N,_N,
          'A1',_N,'A1',_N,'E2','D2','C2',_N,'A1',_N,'G1','A1','E1','F1','G1',_N]),
    # D minor with chromatic neighbours
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.38, 'release': 0.18},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.15, 'release': 0.18,
                             'baseFrequency': 95, 'octaves': 4.2}},
         [_dist(0.58, 0.52)],
         ['D1','D1',_N,'D1','D1','E1','D1',_N,'C1','D1','D1',_N,'D1','D1',_N,'D1',
          'D1','D1',_N,'D1','F1','E1','D1',_N,'C1','B0','A0',_N,'B0','C1','D1',_N]),
    # A minor with chorus shimmer
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.45, 'release': 0.15},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.06, 'sustain': 0.25, 'release': 0.15,
                             'baseFrequency': 130, 'octaves': 5.0}},
         [_dist(0.5, 0.45), _chorus(3, 3.5, 0.5, 0.2)],
         ['A1',_N,'A1','A1','Bb1',_N,'A1',_N,'G1','A1',_N,'A1','G1',_N,'F1','G1',
          'A1','A1',_N,'Bb1','C2',_N,'Bb1','A1','G1',_N,'F1','G1','A1',_N,_N,'G1']),
    # E minor with chromatic descent
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.09, 'sustain': 0.42, 'release': 0.15},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.065, 'sustain': 0.22, 'release': 0.14,
                             'baseFrequency': 125, 'octaves': 5.2}},
         [_dist(0.55, 0.5)],
         ['E1','E1',_N,'E1','F1',_N,'E1',_N,'D1','E1',_N,'E1','D1',_N,'C#1','D1',
          'E1','E1',_N,'F1','G1',_N,'F1','E1','D1',_N,'C#1','D1','E1',_N,_N,'D1']),
    # G minor with filter sweep
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.004, 'decay': 0.07, 'sustain': 0.55, 'release': 0.18},
          'filterEnvelope': {'attack': 0.004, 'decay': 0.055, 'sustain': 0.35, 'release': 0.16,
                             'baseFrequency': 140, 'octaves': 4.8}},
         [_dist(0.65, 0.58), _filt('lowpass', 1500, 4)],
         ['G1',_N,'G1','G1','Ab1','G1',_N,'G1','F1',_N,'G1','F1','Eb1','F1',_N,'G1',
          'G1',_N,'G1','Bb1','G1','Ab1',_N,'G1','F1',_N,'Eb1','F1','G1',_N,_N,'F1'],
         automation=[_auto('effect:1:frequency', 600, 3000, 'tri')]),
]

# ---------------------------------------------------------------------------
# LEADS — industrial stabs / sirens, exactly one per track.
# ---------------------------------------------------------------------------
_LEADS = [
    _cfg('industrial_stab', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.05}},
         [_dist(0.6, 0.6)],
         [_N,'A3',_N,_N,_N,'A3',_N,'G3',_N,_N,_N,'A3',_N,_N,_N,_N,
          _N,'A3',_N,_N,_N,'A3',_N,'G3',_N,'E3',_N,_N,'A3',_N,_N,_N]),
    _cfg('industrial_stab', 'lead', -17, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 25,
          'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0.0, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.1}},
         [_dist(0.7, 0.6)],
         [_N,_N,'A3',_N,_N,'A3',_N,'G3',_N,_N,'A3',_N,_N,_N,_N,_N,
          _N,_N,'A3',_N,_N,'A3',_N,'G3','E3',_N,_N,'A3',_N,_N,_N,_N]),
    _cfg('industrial_stab', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.04}},
         [_dist(0.75, 0.65)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,'A3',_N,_N,_N,_N,_N,
          'A3',_N,_N,_N,_N,_N,'G3',_N,'A3',_N,_N,'G3','E3',_N,_N,_N]),
    _cfg('industrial_stab', 'lead', -16, '16n', 'AMSynth',
         {'harmonicity': 3,
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.0, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.2, 'decay': 0.05, 'sustain': 0, 'release': 0.06}},
         [_dist(0.5, 0.5), _reverb(0.4, 0.2)],
         [_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,'D3',_N,
          _N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,'D3',_N]),
    # Siren — long swept lead
    _cfg('siren', 'lead', -16, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.6, 'release': 0.5}},
         [_dist(0.5, 0.55), _filt('lowpass', 1500, 4), _delay('8n', 0.3, 0.2)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 500, 3500, 'tri')],
         entry_loop=4),
]


# ---------------------------------------------------------------------------
# SUB BASSES — pure sine layer at the lowest octave, providing weight that the
# distorted main bass alone can't deliver. Role 'sub' bypasses sidechain so the
# sub stays full-volume under the kick instead of being ducked away.
# ---------------------------------------------------------------------------
_SUBS = [
    _cfg('sub', 'sub', -8, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.85, 'release': 0.3}},
         [_filt('lowpass', 180, 1)],
         ['A0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N,
          'G0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('sub', 'sub', -7, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.4, 'sustain': 0.9, 'release': 0.3}},
         [_filt('lowpass', 160, 1)],
         ['E0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N,
          'D0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('sub', 'sub', -8, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.004, 'decay': 0.32, 'sustain': 0.88, 'release': 0.3}},
         [_filt('lowpass', 170, 1)],
         ['F0',_N,_N,_N,_N,_N,_N,_N,'F0',_N,_N,_N,_N,_N,_N,_N,
          'Eb0',_N,_N,_N,_N,_N,_N,_N,'F0',_N,_N,_N,_N,_N,_N,_N]),
]


class HardTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HARD_TECHNO
    BPM_RANGE = (145, 153)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        lead = copy.deepcopy(cls._pick(_LEADS))
        sub = copy.deepcopy(cls._pick(_SUBS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.25, ghost_prob=0.08)
        lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
        sub['pattern']['velocities'] = _vel(sub['pattern']['steps'], accent_prob=0.1, ghost_prob=0.0)

        layers = [kick, snare, hihat, bass, lead, sub]
        cls._apply_key_coherence(layers)
        return layers

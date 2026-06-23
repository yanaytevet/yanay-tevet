import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus, _filt, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

# ---------------------------------------------------------------------------
# KICKS — long deep sub kicks, Berlin warehouse style. Subtle variance only.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.7}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.8}},
         [_reverb(1.0, 0.12)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'envelope': {'attack': 0.001, 'decay': 0.46, 'sustain': 0.01, 'release': 1.55}, 'octaves': 9},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Anticipation kick on step 15 — adds bar-2 push
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.3}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# SNARES / CLAPS — backbeats on 2 & 4, occasional ghost.
# ---------------------------------------------------------------------------
_SNARES = [
    _cfg('snare', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.05}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.4, 0.25)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.2, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.6, 0.35)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Ghost on "and" of 2 in bar 2
    _cfg('snare', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.5, 0.3)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Rimshot — high pitch, very sparse
    _cfg('snare', 'snare', -12, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.6, 0.25)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — closed metallic, mostly 8th-note or off-beat patterns.
# Velocities via _vel_groove for groove feel.
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.01},
          'harmonicity': 4.5, 'modulationIndex': 28, 'resonance': 4500, 'octaves': 1.5},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.045, 'release': 0.025},
          'harmonicity': 4.0, 'modulationIndex': 24, 'resonance': 4200, 'octaves': 1.4},
         [],
         ['C4',_N,_N,'C4','C4',_N,'C4',_N,'C4',_N,_N,'C4','C4',_N,'C4',_N,
          'C4',_N,_N,'C4','C4',_N,'C4',_N,'C4',_N,_N,'C4','C4',_N,'C4',_N]),
    # Offbeat hat
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 490, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015},
          'harmonicity': 4.5, 'modulationIndex': 27, 'resonance': 4700, 'octaves': 1.45},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.012},
          'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 6500, 'octaves': 1.6},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,_N,_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,_N,_N]),
    # Open-hat feel on offbeat
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 520, 'envelope': {'attack': 0.001, 'decay': 0.12, 'release': 0.08},
          'harmonicity': 3.8, 'modulationIndex': 22, 'resonance': 4000, 'octaves': 1.3},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# BASSES — sub-rooted, often with filter automation for the slow movement.
# Detroit-style minor scales with chromatic motion.
# ---------------------------------------------------------------------------
_BASSES = [
    # A minor sustained — filter sweep adds movement
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.4, 'release': 0.3},
          'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.2, 'release': 0.3,
                             'baseFrequency': 100, 'octaves': 2}},
         [_filt('lowpass', 800, 3)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,_N,
          'G1',_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 250, 1800, 'tri')]),
    # E minor walking
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.03, 'decay': 0.35, 'sustain': 0.35, 'release': 0.3},
          'filterEnvelope': {'attack': 0.03, 'decay': 0.45, 'sustain': 0.15, 'release': 0.3,
                             'baseFrequency': 90, 'octaves': 2.2}},
         [_filt('lowpass', 700, 3)],
         ['E1',_N,_N,_N,_N,_N,_N,_N,'D1',_N,_N,_N,_N,_N,_N,_N,
          'E1',_N,_N,_N,_N,_N,_N,_N,'B0',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 200, 1600, 'tri')]),
    # D minor stepwise — more melodic
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.025, 'decay': 0.4, 'sustain': 0.3, 'release': 0.3},
          'filterEnvelope': {'attack': 0.025, 'decay': 0.5, 'sustain': 0.1, 'release': 0.3,
                             'baseFrequency': 80, 'octaves': 2.5}},
         [_filt('lowpass', 750, 3.5)],
         ['D1',_N,_N,_N,'D1',_N,'D1',_N,_N,_N,'D1',_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,'D1',_N,_N,_N,'C1',_N,'Bb0',_N,_N,_N]),
    # F minor sub pulse
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.025, 'decay': 0.38, 'sustain': 0.32, 'release': 0.3},
          'filterEnvelope': {'attack': 0.025, 'decay': 0.5, 'sustain': 0.1, 'release': 0.3,
                             'baseFrequency': 95, 'octaves': 2}},
         [_filt('lowpass', 700, 3)],
         ['F1',_N,_N,_N,_N,_N,_N,_N,'F1',_N,_N,_N,_N,_N,_N,_N,
          'Eb1',_N,_N,_N,_N,_N,_N,_N,'F1',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 250, 1700, 'tri')]),
    # A minor walking with chromatic neighbours — Berlin warehouse style
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.35, 'release': 0.25},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.25, 'release': 0.25,
                             'baseFrequency': 90, 'octaves': 2.5}},
         [_filt('lowpass', 800, 3)],
         ['A0',_N,'A0',_N,_N,'A0',_N,_N,'G0',_N,'A0',_N,_N,_N,'G0',_N,
          'A0',_N,'A0',_N,'B0','A0',_N,_N,'G0','A0',_N,_N,'F#0',_N,'G0',_N]),
    # E minor walking
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.012, 'decay': 0.22, 'sustain': 0.3, 'release': 0.28},
          'filterEnvelope': {'attack': 0.012, 'decay': 0.28, 'sustain': 0.2, 'release': 0.25,
                             'baseFrequency': 85, 'octaves': 2.8}},
         [_filt('lowpass', 750, 3.2)],
         ['E1',_N,'E1',_N,_N,'E1',_N,_N,'D1',_N,'E1',_N,_N,_N,'D1',_N,
          'E1',_N,'E1',_N,'F#1','E1',_N,_N,'D1','E1',_N,_N,'C#1',_N,'D1',_N]),
    # Triangle deep — sub presence
    _cfg('bass', 'bass', -8, '8n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.03, 'decay': 0.4, 'sustain': 0.5, 'release': 0.35},
          'filterEnvelope': {'attack': 0.03, 'decay': 0.5, 'sustain': 0.3, 'release': 0.35,
                             'baseFrequency': 70, 'octaves': 1.8}},
         [],
         ['A0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# LEADS — sparse stabs or evolving pads. The atmospheric voice of techno.
# ---------------------------------------------------------------------------
_LEADS = [
    _cfg('stab', 'lead', -16, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.5, 0.3)],
         [_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,
          _N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N]),
    _cfg('stab', 'lead', -20, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.5, 'release': 0.6}},
         [_reverb(3.5, 0.7, 0.04), _chorus(0.8, 4, 0.6, 0.4)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'D3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -20, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.4, 'decay': 0.5, 'sustain': 0.45, 'release': 0.6}},
         [_reverb(4.5, 0.75, 0.06), _chorus(0.5, 5, 0.5, 0.4)],
         ['F3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'Eb3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('stab', 'lead', -16, '16n', 'AMSynth',
         {'harmonicity': 1.0,
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.0, 'release': 0.2},
          'modulationEnvelope': {'attack': 0.3, 'decay': 0.1, 'sustain': 0.5, 'release': 0.3}},
         [_reverb(1.8, 0.45)],
         [_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,
          _N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,'F#3',_N,_N,_N]),
    # FM stab with sweep
    _cfg('stab', 'lead', -17, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 10,
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.06},
          'modulationEnvelope': {'attack': 0.3, 'decay': 0.05, 'sustain': 0, 'release': 0.05}},
         [_reverb(1.2, 0.35), _filt('lowpass', 3000, 2)],
         [_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 800, 4500, 'tri')]),
]

# ---------------------------------------------------------------------------
# FILLS — sparse accents gated by loop_modulo so they fire every N loops only.
# Each loop = 2 bars, so loop_modulo=8 fires once every 16 bars (one "phrase").
# ---------------------------------------------------------------------------
_FILLS = [
    # 16-step snare roll on the last beat of bar 2, every 16 bars
    _cfg('fill_roll', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [_reverb(0.5, 0.35)],
         [_N]*28 + ['C2', 'C2', 'C2', 'C2'],
         loop_modulo=8, loop_modulo_remainder=7),
    # Reverse-cymbal style swell, every 8 bars
    _cfg('fill_swell', 'perc', -16, '1n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.5, 'decay': 0.1, 'sustain': 0.9, 'release': 0.2}},
         [_reverb(2.0, 0.5), _filt('highpass', 1500, 1)],
         ['C3'] + [_N]*31,
         loop_modulo=4, loop_modulo_remainder=3),
    # Tom-style descending hit on the last quarter, every 16 bars
    _cfg('fill_tom', 'perc', -10, '8n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.4}},
         [_reverb(0.8, 0.35)],
         [_N]*24 + ['G1', _N, 'E1', _N, 'C1', _N, 'A0', _N],
         loop_modulo=8, loop_modulo_remainder=7),
]

# ---------------------------------------------------------------------------
# PERCS — optional accent layer
# ---------------------------------------------------------------------------
_PERCS = [
    _cfg('perc', 'perc', -16, '16n', 'MetalSynth',
         {'frequency': 200, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.03},
          'harmonicity': 4.0, 'modulationIndex': 25, 'resonance': 3000, 'octaves': 1.5},
         [_dist(0.4, 0.35)],
         [_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('perc', 'perc', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.8, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('perc', 'perc', -15, '16n', 'MetalSynth',
         {'frequency': 250, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 3.5, 'modulationIndex': 20, 'resonance': 3500, 'octaves': 1.2},
         [],
         [_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,
          _N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N]),
]


class TechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.TECHNO
    BPM_RANGE = (130, 138)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        lead = copy.deepcopy(cls._pick(_LEADS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.08)
        lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.25, ghost_prob=0.0)

        # Lead may enter late — leaves room for the groove to establish
        if random.random() < 0.5:
            lead['entry_loop'] = random.choice([2, 4])

        layers = [kick, snare, hihat, bass, lead]

        perc = cls._maybe(_PERCS, 0.4)
        if perc:
            layers.append(copy.deepcopy(perc))

        # Occasional phrase fill (snare roll / swell / tom run) — gated by loop_modulo,
        # so it only fires once every N loops instead of every bar.
        fill = cls._maybe(_FILLS, 0.55)
        if fill:
            layers.append(copy.deepcopy(fill))

        cls._apply_key_coherence(layers)
        return layers

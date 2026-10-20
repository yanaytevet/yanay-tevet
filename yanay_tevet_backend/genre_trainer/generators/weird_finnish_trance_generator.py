import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay, _dist, _filt, _chorus, _auto, _pingpong, _vel,
    _vel_groove, _vel_kick, _vel_snare, _four, _roll,
)

# Accent positions of a 3+3+2 grouping inside each 8-step half bar.
_ACCENTS_332 = frozenset({0, 3, 6})


def _vel_332(steps: list) -> list[float | None]:
    """Accents on a 3+3+2 grouping of 16ths, everything else medium. Laid over a four-on-the-floor
    kick it makes the line lurch against the beat — the lopsided bounce of suomisaundi."""
    vels: list[float | None] = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 8 in _ACCENTS_332:
            vels.append(round(random.uniform(0.85, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.45, 0.65), 2))
    return vels


# ---------------------------------------------------------------------------
# KICKS — strict four-on-the-floor, rounder and less brutal than dark psy so
# the silliness on top stays the focus.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0, 'release': 0.08}},
         [], _four('A1')),
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 5,
          'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0, 'release': 0.08}},
         [], _four('G1')),
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.27, 'sustain': 0, 'release': 0.06}},
         [_dist(0.25, 0.3)], _four('A1')),
    # Bouncier, slightly boomy — the pitch sweep itself has a "boing" to it
    _cfg('kick', 'kick', -1, '16n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 5,
          'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0, 'release': 0.08}},
         [], _four('F#1')),
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0, 'release': 0.07}},
         [_filt('lowpass', 4000, 0.7)], _four('B1')),
]

# ---------------------------------------------------------------------------
# CLAPS — optional backbeat on 2 & 4, one with a cheeky pickup.
# ---------------------------------------------------------------------------
_CLAPS = [
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 900, 0.8)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.8, 0.3)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 1100, 0.8)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — off-beat open hats and 16ths, plus a 3+3+2 hat that tips the
# groove sideways.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Off-beat open hat
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.08, 'release': 0.05},
          'harmonicity': 3.0, 'modulationIndex': 16, 'resonance': 7000, 'octaves': 1.2},
         [], [_N,_N,'C4',_N] * 8),
    # Closed 16ths
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 950, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008},
          'harmonicity': 9.0, 'modulationIndex': 55, 'resonance': 8500, 'octaves': 2.2},
         [], ['C4'] * 32),
    # 3+3+2 hat — hits on the odd grouping instead of the off-beats
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 7500, 'octaves': 1.5},
         [], ['C4',_N,_N,'C4',_N,_N,'C4',_N] * 4),
    # Off-beat open hat with a 16th pickup into every second beat
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.03},
          'harmonicity': 3.5, 'modulationIndex': 18, 'resonance': 7200, 'octaves': 1.3},
         [], [_N,_N,'C4',_N,_N,_N,'C4','C4'] * 4),
    # Shaker ticks — noise 16ths skipping the kick
    _cfg('hihat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 7000, 0.8)], [_N,'C4','C4','C4'] * 8),
]

# ---------------------------------------------------------------------------
# BASSES — bouncy, rubbery, never on the kick and never a held sine. Either
# the rolling K-B-B-B with octave and arpeggio leaps, or an off-beat pair that
# hops an octave. Major and mixolydian movement (I - bVII - IV) instead of
# psy's Phrygian. Written on A1; key coherence keeps the register.
# ---------------------------------------------------------------------------
_BOING_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'type': 'lowpass', 'Q': 5, 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.11, 'sustain': 0, 'release': 0.04},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.09, 'sustain': 0, 'release': 0.04,
                       'baseFrequency': 140, 'octaves': 3.2},
}
# Unison FM with a slow-ish modulation decay: every note "boings" from bright to round
_RUBBER_FM = {
    'harmonicity': 1, 'modulationIndex': 7,
    'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.04},
    'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.04},
}
_PLUCK_SAW = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'type': 'lowpass', 'Q': 4, 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.04},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.07, 'sustain': 0, 'release': 0.04,
                       'baseFrequency': 180, 'octaves': 3},
}

_BASSES = [
    # Octave bounce roll — I, bVII, IV, V: a cheerful mixolydian loop
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _BOING_SQUARE,
         [_dist(0.25, 0.25), _filt('lowpass', 1400, 2)],
         _roll('A1 A2 A1', 'A1 A2 A1', 'A1 A2 A1', 'A1 A2 A1',
               'G1 G2 G1', 'G1 G2 G1', 'D2 D3 D2', 'E2 E3 E2')),
    # Off-beat hop — silent on the kick and the 16th after it, then a pair jumping up an octave
    _cfg('bass', 'bass', -4, '16n', 'FMSynth', _RUBBER_FM,
         [_filt('lowpass', 1600, 2)],
         _roll('- A1 A2', '- A1 A2', '- A1 A2', '- C2 C3',
               '- A1 A2', '- A1 A2', '- G1 G2', '- E2 E3')),
    # Major roll — up through the major third and fifth, a chromatic climb back home
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _PLUCK_SAW,
         [_dist(0.2, 0.2), _filt('lowpass', 1500, 2)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'C#2 C#2 C#2', 'E2 E2 E2',
               'A1 A1 A1', 'A1 A1 A1', 'G1 G1 G1', 'F#1 G1 G#1'),
         automation=[_auto('effect:1:frequency', 700, 2200, 'tri')]),
    # Arpeggio roll — root, fifth, octave in every beat: a springy cartoon gallop through I, bVII, IV, V
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _RUBBER_FM,
         [_filt('lowpass', 1800, 2)],
         _roll('A1 E2 A2', 'A1 E2 A2', 'A1 E2 A2', 'G1 D2 G2',
               'A1 E2 A2', 'A1 E2 A2', 'D2 A2 D3', 'E2 B2 E3')),
    # 3+3+2 pops — the octave jumps land on the odd grouping, so the line lurches against the kick
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _BOING_SQUARE,
         [_dist(0.2, 0.2), _filt('lowpass', 1500, 3)],
         _roll('A1 A1 A2', 'A1 A2 A1', 'A1 A1 A2', 'A1 A2 A1',
               'G1 G1 G2', 'G1 G2 G1', 'C2 C2 C3', 'D2 D3 D2')),
    # Waddle — chromatic neighbours, then a major scale run up to the fifth and back
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _PLUCK_SAW,
         [_dist(0.25, 0.25), _filt('lowpass', 1300, 3)],
         _roll('A1 A1 A1', 'Bb1 A1 A1', 'A1 A1 A1', 'G#1 A1 A1',
               'A1 A1 A1', 'B1 C#2 D2', 'E2 E2 E2', 'E2 D2 C#2'),
         automation=[_auto('effect:1:frequency', 800, 2400, 'tri')]),
]

# ---------------------------------------------------------------------------
# LEADS — the genre. Melodies that leap (octaves, sixths, tritones), major and
# mixolydian with a lydian #4 here and there, phrased on 3+3+2 rather than
# square fours, and voiced by cartoon instruments: detuned FM bells, squeaky
# resonant squares, swooping portamento, a kazoo. Each has A as its most
# frequent note so key coherence keeps the tune intact.
# ---------------------------------------------------------------------------
# Slightly off-integer ratio: the bell partials beat against each other, a music-box out of tune
_DETUNED_BELL = {
    'harmonicity': 3.01, 'modulationIndex': 10,
    'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0, 'release': 0.3},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.2},
}
_SQUEAKY_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'type': 'lowpass', 'Q': 16, 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.1, 'release': 0.06},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.1, 'release': 0.06,
                       'baseFrequency': 600, 'octaves': 3},
}
# Portamento makes every leap a slide-whistle swoop
_SWOOP = {
    'oscillator': {'type': 'triangle'}, 'portamento': 0.07,
    'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.3, 'release': 0.1},
}

_LEADS = [
    # Bell leaps — root, fifth, octave, b7 on a 3+3+2 grid
    _cfg('bell_leaps', 'lead', -11, '16n', 'FMSynth', _DETUNED_BELL,
         [_chorus(2, 3.5, 0.5, 0.4), _delay('8n.', 0.3, 0.25), _reverb(1.5, 0.25)],
         ['A4',_N,_N,'E5',_N,_N,'A5',_N,'G5',_N,_N,'E5',_N,_N,'C#5',_N,
          'A4',_N,_N,'F#5',_N,_N,'A5',_N,'B5',_N,_N,'G5',_N,_N,'E5',_N]),
    # Squeak — a resonant square hopping octaves and fourths, its filter swept wide open
    _cfg('squeak', 'lead', -13, '16n', 'MonoSynth', _SQUEAKY_SQUARE,
         [_filt('lowpass', 3000, 6), _delay('16n', 0.25, 0.15)],
         ['A4',_N,'A5',_N,_N,'E5',_N,'A5',_N,'D5',_N,_N,'A4',_N,'G5',_N,
          'A4',_N,'A5',_N,_N,'F#5',_N,'A5',_N,'C#6',_N,'B5',_N,'A5',_N,_N],
         automation=[_auto('effect:0:frequency', 1200, 5000, 'tri')]),
    # Swoop — every leap slides, octave up, down to the fifth, a sixth below
    _cfg('swoop', 'lead', -11, '8n', 'Synth', _SWOOP,
         [_delay('8n', 0.3, 0.2), _reverb(1.2, 0.2)],
         ['A4',_N,_N,'A5',_N,_N,'E5',_N,_N,_N,'A4',_N,'D5',_N,_N,_N,
          'A4',_N,_N,'A5',_N,_N,'G5',_N,_N,_N,'E5',_N,'A5',_N,_N,_N]),
    # Circus — a lydian run with the #4 and a whole-tone slip, then a big drop
    _cfg('circus', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 4,
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.2, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.2, 'release': 0.1}},
         [_delay('8n', 0.25, 0.15)],
         ['A4','B4','C#5','D#5',_N,'F5',_N,'D#5','A4',_N,'E5',_N,'A4',_N,_N,_N,
          'A5',_N,'G5',_N,'E5',_N,'A4',_N,'D#5',_N,'E5',_N,'A4',_N,_N,_N]),
    # Kazoo — a nasal pulse-width buzz chattering a mixolydian riff
    _cfg('kazoo', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'pwm', 'modulationFrequency': 6},
          'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.3, 'release': 0.05}},
         [_filt('bandpass', 1500, 2), _reverb(0.8, 0.15)],
         ['A4','A4',_N,'G4','A4',_N,'C#5',_N,'A4',_N,_N,'E5',_N,_N,'D5',_N,
          'A4','A4',_N,'G4','A4',_N,'E5',_N,'F#5',_N,_N,'E5',_N,_N,'A4',_N]),
    # Boing lead — FM with a lingering modulation decay so every note wobbles; leaps of a sixth and octave
    _cfg('boing_lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 12,
          'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.05, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0, 'release': 0.1}},
         [_pingpong('8n', 0.3, 0.2)],
         ['A4',_N,_N,'F#5',_N,_N,'A5',_N,'A4',_N,_N,'E5',_N,_N,'C#6',_N,
          'A5',_N,_N,'A4',_N,_N,'G5',_N,'A4',_N,_N,'D5',_N,_N,'A5',_N]),
]

# ---------------------------------------------------------------------------
# CALL AND RESPONSE — pairs of motifs on the same voice that take turns, one
# loop each (loop_modulo 2), so the tune keeps changing its mind.
# ---------------------------------------------------------------------------
_CALL_RESPONSES = [
    # Bell: a rising question, a falling mixolydian answer
    (_cfg('bell_call', 'lead', -11, '16n', 'FMSynth', _DETUNED_BELL,
          [_delay('8n.', 0.3, 0.25), _reverb(1.5, 0.25)],
          ['A4',_N,_N,'C#5',_N,_N,'E5',_N,'A5',_N,_N,_N,_N,_N,_N,_N,
           'A4',_N,_N,'C#5',_N,_N,'E5',_N,'B5',_N,_N,'A5',_N,_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=0),
     _cfg('bell_answer', 'lead', -11, '16n', 'FMSynth', _DETUNED_BELL,
          [_delay('8n.', 0.3, 0.25), _reverb(1.5, 0.25)],
          ['A5',_N,_N,'G5',_N,_N,'E5',_N,'D5',_N,_N,_N,_N,_N,_N,_N,
           'A5',_N,_N,'G5',_N,_N,'D5',_N,'A4',_N,_N,_N,'A4',_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=1)),
    # Squeak: high stutter, then a low grumble that leaps back up
    (_cfg('squeak_call', 'lead', -13, '16n', 'MonoSynth', _SQUEAKY_SQUARE,
          [_delay('16n', 0.25, 0.15)],
          ['A5','A5',_N,'E5',_N,_N,'A5',_N,'A5','A5',_N,'F#5',_N,_N,'A5',_N,
           'A5','A5',_N,'E5',_N,_N,'A5',_N,'C#6',_N,_N,'A5',_N,_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=0),
     _cfg('squeak_answer', 'lead', -13, '16n', 'MonoSynth', _SQUEAKY_SQUARE,
          [_delay('16n', 0.25, 0.15)],
          ['A4',_N,_N,'B4',_N,_N,'C#5',_N,'A4',_N,_N,_N,'A5',_N,_N,_N,
           'A4',_N,_N,'G4',_N,_N,'A4',_N,'E5',_N,_N,_N,'A5',_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=1)),
    # Swoop: up an octave and a tritone, then gliding back down through the major sixth
    (_cfg('swoop_call', 'lead', -11, '8n', 'Synth', _SWOOP,
          [_delay('8n', 0.3, 0.2)],
          ['A4',_N,_N,'A5',_N,_N,'D#5',_N,'A4',_N,_N,_N,_N,_N,_N,_N,
           'A4',_N,_N,'A5',_N,_N,'E5',_N,'A4',_N,_N,_N,_N,_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=0),
     _cfg('swoop_answer', 'lead', -11, '8n', 'Synth', _SWOOP,
          [_delay('8n', 0.3, 0.2)],
          ['A5',_N,_N,'F#5',_N,_N,'A4',_N,_N,_N,_N,_N,'C#5',_N,_N,_N,
           'A5',_N,_N,'F#5',_N,_N,'E5',_N,_N,_N,_N,_N,'A4',_N,_N,_N],
          loop_modulo=2, loop_modulo_remainder=1)),
]

# ---------------------------------------------------------------------------
# STABS — optional happy chords off the beat: major, sus4 and a bVII, never
# the minor-key drama of trance.
# ---------------------------------------------------------------------------
_STABS = [
    # Major off-beat skank, I to bVII in bar 2
    _cfg('happy_stab', 'stab', -17, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.08}},
         [_filt('lowpass', 2500, 1), _reverb(1.0, 0.2)],
         [_N,_N,'A3,C#4,E4',_N,_N,_N,'A3,C#4,E4',_N,_N,_N,'A3,C#4,E4',_N,_N,_N,'A3,C#4,E4',_N,
          _N,_N,'G3,B3,D4',_N,_N,_N,'G3,B3,D4',_N,_N,_N,'A3,C#4,E4',_N,_N,_N,'A3,C#4,E4',_N]),
    # Organ fifths on the 3+3+2 grid
    _cfg('organ_fifths', 'stab', -18, '16n', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.1, 'release': 0.1}},
         [_chorus(3, 2.5, 0.4, 0.3)],
         ['A3,E4',_N,_N,'A3,E4',_N,_N,'A3,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A3,E4',_N,_N,'A3,E4',_N,_N,'G3,D4',_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Detuned sus4 — a wide, wobbly unresolved chord, now and then
    _cfg('wonky_sus', 'stab', -18, '8n', 'PolySynth',
         {'oscillator': {'type': 'fatsawtooth', 'spread': 30, 'count': 3},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.1, 'release': 0.2}},
         [_filt('lowpass', 2000, 1), _reverb(1.8, 0.3)],
         [_N,_N,_N,_N,_N,_N,'A3,D4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'A3,D4,E4',_N,_N,_N,'A3,C#4,E4',_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# ODDBALLS — the out-of-place sound: a laser "pew", a slide whistle, a squeaky
# toy, a quack, a spring boing, a squeaky resonant sweep. Percussion by role,
# so they stay off-key on purpose; each turns up only on some loops.
# ---------------------------------------------------------------------------
_ODDBALLS = [
    # Laser pew — a membrane pitched high and dropping fast
    _cfg('pew', 'perc', -16, '16n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 3,
          'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.1}},
         [_pingpong('8n', 0.3, 0.25)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A4',_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A4',_N],
         dropout_prob=0.5),
    # Slide whistle — a sine gliding up an octave and tumbling down, every fourth loop
    _cfg('slide_whistle', 'perc', -17, '8n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'portamento': 0.25,
          'envelope': {'attack': 0.02, 'decay': 0.2, 'sustain': 0.6, 'release': 0.1}},
         [_reverb(1.0, 0.2)],
         [_N] * 24 + ['A5', _N, 'A6', _N, 'E5', _N, _N, _N],
         loop_modulo=4, loop_modulo_remainder=3),
    # Squeaky toy — two high FM chirps
    _cfg('squeaky_toy', 'perc', -18, '32n', 'FMSynth',
         {'harmonicity': 6.01, 'modulationIndex': 6,
          'envelope': {'attack': 0.002, 'decay': 0.06, 'sustain': 0, 'release': 0.03},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.04, 'sustain': 0, 'release': 0.02}},
         [],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'C#7','A6',_N,_N,_N,_N,_N,_N,'C#7','A6'],
         dropout_prob=0.4),
    # Quack — a low FM honk through a nasal band-pass, every other loop
    _cfg('quack', 'perc', -15, '16n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 12,
          'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_filt('bandpass', 900, 6)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3','A3',_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         loop_modulo=2, loop_modulo_remainder=1),
    # Spring boing — a low membrane with a long, slow pitch drop
    _cfg('spring_boing', 'perc', -14, '8n', 'MembraneSynth',
         {'pitchDecay': 0.2, 'octaves': 2,
          'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0, 'release': 0.2}},
         [],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N],
         dropout_prob=0.5),
    # Squeaky resonant sweep — noise through a razor-thin band-pass shooting up the spectrum
    _cfg('squeak_sweep', 'perc', -19, '4n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.4, 'release': 0.1}},
         [_filt('bandpass', 800, 25)],
         [_N] * 24 + ['C4'] + [_N] * 7,
         automation=[_auto('effect:0:frequency', 600, 7000, 'ramp')],
         loop_modulo=2, loop_modulo_remainder=0),
]


class WeirdFinnishTranceTrackGenerator(BaseTrackGenerator):
    """Suomisaundi: psy's four-on-the-floor and off-kick bass, played for laughs — leaping major-key
    tunes on cartoon voices, lopsided 3+3+2 accents, and something silly every few loops."""
    GENRE = GenreType.WEIRD_FINNISH_TRANCE
    BPM_RANGE = (142, 150)
    LEVEL_DB = -2.1
    KEY_ROLES = ('lead', 'bass')
    SIDECHAIN_DEPTH = 0.8
    SIDECHAIN_RELEASE = 0.25

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass_steps = bass['pattern']['steps']
        bass['pattern']['velocities'] = (
            _vel_332(bass_steps) if random.random() < 0.5 else _vel(bass_steps, accent_prob=0.25, ghost_prob=0.0)
        )
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        layers = [kick, bass, hihat]

        clap = cls._maybe(_CLAPS, 0.6)
        if clap is not None:
            clap = copy.deepcopy(clap)
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        if random.random() < 0.35:
            leads = [copy.deepcopy(motif) for motif in random.choice(_CALL_RESPONSES)]
        else:
            leads = [copy.deepcopy(cls._pick(_LEADS))]
        for lead in leads:
            lead['pattern']['velocities'] = _vel_332(lead['pattern']['steps'])
        layers.extend(leads)

        oddball = cls._maybe(_ODDBALLS, 0.75)
        if oddball is not None:
            oddball = copy.deepcopy(oddball)
            oddball['pattern']['velocities'] = _vel(oddball['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
            layers.append(oddball)

        stab = cls._maybe(_STABS, 0.4)
        if stab is not None:
            stab = copy.deepcopy(stab)
            stab['pattern']['velocities'] = _vel_332(stab['pattern']['steps'])
            layers.append(stab)

        cls._apply_key_coherence(layers)
        return layers

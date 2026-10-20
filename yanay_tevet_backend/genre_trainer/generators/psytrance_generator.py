import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _pingpong, _auto, _vel,
    _vel_groove, _slides, _on, _vel_flat, _vel_kick, _rolling, _vel_roll,
)

_STEPS = 32


# Inside each beat the 16th straight after the kick sits back (it lands on the kick's tail and the
# duck's recovery), the middle 16th leads. Psy bass is machine-even otherwise — no ghosts, no accents.
_ROLL_LEVELS = {1: (0.8, 0.86), 2: (0.9, 0.97), 3: (0.85, 0.91)}


# ---------------------------------------------------------------------------
# KICKS — strict four-on-the-floor, short and punchy. A fast pitch drop gives
# the click; the body has to be gone before the first bass 16th, so decays stay
# around a quarter second with no sustain. Tuning varies (F1–G#1) for colour.
# ---------------------------------------------------------------------------
_KICKS = [
    # Tight punch — the reference full-on kick
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0, 'release': 0.06}},
         [], _on(range(0, _STEPS, 4), 'G1')),
    # Clicky — faster, higher sweep: more attack on small speakers
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.016, 'octaves': 9,
          'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0, 'release': 0.05}},
         [], _on(range(0, _STEPS, 4), 'A1')),
    # Saturated — drive thickens the body without lengthening it
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.06}},
         [_dist(0.22, 0.3)], _on(range(0, _STEPS, 4), 'F#1')),
    # Round — slower sweep, lower tuning, still short enough to leave the roll room
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.034, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.29, 'sustain': 0, 'release': 0.07}},
         [], _on(range(0, _STEPS, 4), 'F1')),
    # Triangle body — odd harmonics make the thump readable on laptops; lowpass keeps it clean
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 8, 'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0, 'release': 0.05}},
         [_filt('lowpass', 2800, 0.7)], _on(range(0, _STEPS, 4), 'G1')),
    # Short and dry — the tightest variant, suits the top of the tempo range
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 0.19, 'sustain': 0, 'release': 0.04}},
         [], _on(range(0, _STEPS, 4), 'G#1')),
]

# ---------------------------------------------------------------------------
# BASSES — the rolling K-B-B-B that defines full-on: three short 16ths after
# every kick, nothing on it. Short plucks (decay ~0.1, no sustain) so each note
# is separate; light drive into a resonant lowpass whose opening is automated
# over the loop. Mostly the root — the fills are phrygian / harmonic-minor
# passing notes in the last beat of bar 2. All written on A1; key coherence
# moves them within E1–Eb2, the full-on bass register.
# ---------------------------------------------------------------------------
# FM at harmonicity 0.5 with a fast-collapsing index: a bright "tok" on the attack, sine body after.
_FM_ROLL = {
    'harmonicity': 0.5, 'modulationIndex': 12,
    'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.03},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.03},
}
# Square modulator and some held index: buzzier and more aggressive.
_FM_ROLL_GRIT = {
    'harmonicity': 0.5, 'modulationIndex': 18, 'modulation': {'type': 'square'},
    'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.03},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.15, 'release': 0.03},
}
# Saw through a snappy filter envelope: the other classic full-on bass patch.
_SAW_ROLL = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 2, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 180, 'octaves': 3.5},
}

_BASSES = [
    # One-note roll — the pure form
    _cfg('bass', 'bass', -6, '16n', 'FMSynth', _FM_ROLL,
         [_dist(0.25, 0.3), _filt('lowpass', 900, 5)],
         _rolling('A1'),
         automation=[_auto('effect:1:frequency', 300, 1800, 'tri')]),
    # Octave kick-back — the last 16th of each bar jumps up, pushing into the next downbeat
    _cfg('bass', 'bass', -7, '16n', 'FMSynth', _FM_ROLL_GRIT,
         [_dist(0.3, 0.32), _filt('lowpass', 850, 5)],
         _rolling('A1', {15: 'A2', 31: 'A2'}),
         automation=[_auto('effect:1:frequency', 350, 2000, 'tri')]),
    # Phrygian walk-down — minor third, flat second, home
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SAW_ROLL,
         [_dist(0.2, 0.28), _filt('lowpass', 800, 6)],
         _rolling('A1', {29: 'C2', 30: 'Bb1'}),
         automation=[_auto('effect:1:frequency', 400, 2200, 'ramp')]),
    # Flat-seven drop — the whole last beat steps down a tone
    _cfg('bass', 'bass', -6, '16n', 'FMSynth', _FM_ROLL,
         [_dist(0.28, 0.3), _filt('lowpass', 880, 5)],
         _rolling('A1', {29: 'G1', 30: 'G1', 31: 'G1'}),
         automation=[_auto('effect:1:frequency', 280, 1700, 'tri')]),
    # Harmonic-minor turn — flat six, five, leading tone back up to the root
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SAW_ROLL,
         [_dist(0.22, 0.3), _filt('lowpass', 820, 5)],
         _rolling('A1', {29: 'F1', 30: 'E1', 31: 'G#1'}),
         automation=[_auto('effect:1:frequency', 320, 1900, 'tri')]),
    # Breath before the downbeat — octave lift, then one 16th of silence
    _cfg('bass', 'bass', -7, '16n', 'FMSynth', _FM_ROLL_GRIT,
         [_dist(0.25, 0.3), _filt('lowpass', 900, 5)],
         _rolling('A1', {30: 'A2', 31: _N}),
         automation=[_auto('effect:1:frequency', 300, 2100, 'tri')]),
    # Third and second — two beats of movement closing the phrase
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SAW_ROLL,
         [_dist(0.24, 0.3), _filt('lowpass', 780, 6)],
         _rolling('A1', {25: 'C2', 26: 'C2', 27: 'C2', 29: 'Bb1', 30: 'Bb1', 31: 'Bb1'}),
         automation=[_auto('effect:1:frequency', 350, 2400, 'ramp')]),
]

# ---------------------------------------------------------------------------
# OPEN HATS — the "tss" on every offbeat (the 3rd 16th of each beat), right
# between the kick and the next one. Filtered noise: bright, short tail.
# ---------------------------------------------------------------------------
_OFFBEATS = range(2, _STEPS, 4)

_OPEN_HATS = [
    # Classic — bright white noise, short tail
    _cfg('open_hat', 'hihat', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 7500, 0.9)], _on(_OFFBEATS, 'C4')),
    # Ringing — a resonant highpass adds a metallic edge
    _cfg('open_hat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 8200, 5)], _on(_OFFBEATS, 'C4')),
    # Long sizzle — longer decay plus a little room
    _cfg('open_hat', 'hihat', -17, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0, 'release': 0.06}},
         [_filt('highpass', 9000, 0.8), _reverb(0.8, 0.12)], _on(_OFFBEATS, 'C4')),
    # Pink body — darker, fuller hat
    _cfg('open_hat', 'hihat', -13, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.11, 'sustain': 0, 'release': 0.04}},
         [_filt('bandpass', 8500, 1.2)], _on(_OFFBEATS, 'C4')),
    # Short chick — tight, for the busier tracks
    _cfg('open_hat', 'hihat', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 6500, 1)], _on(_OFFBEATS, 'C4')),
    # FM metal — an inharmonic FM cluster above a highpass: the 909-ish metallic open hat
    _cfg('open_hat', 'hihat', -19, '16n', 'FMSynth',
         {'harmonicity': 5.1, 'modulationIndex': 40,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.04},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 6000, 1)], _on(_OFFBEATS, 'A5')),
]

# ---------------------------------------------------------------------------
# CLOSED HATS — 16th ticks under the open hat; the groove velocities put the
# weight on the beat and keep the in-between 16ths quiet.
# ---------------------------------------------------------------------------
_CLOSED_HATS = [
    # Straight 16ths
    _cfg('closed_hat', 'hihat', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.025, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 9500, 0.8)], _on(range(_STEPS), 'C4'), pan=-0.2),
    # Around the open hat — leaves the offbeat to it
    _cfg('closed_hat', 'hihat', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 9000, 1)], _on((i for i in range(_STEPS) if i % 4 != 2), 'C4'), pan=-0.2),
    # Off-16th ticks — only the "e" and "a" of each beat
    _cfg('closed_hat', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 10000, 1)], _on(range(1, _STEPS, 2), 'C4'), pan=-0.25),
    # FM tick 16ths — glassier, more metallic
    _cfg('closed_hat', 'hihat', -25, '16n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 22,
          'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 7000, 1)], _on(range(_STEPS), 'C7'), pan=-0.15),
    # Off the kick — 16ths that drop out where the kick lands
    _cfg('closed_hat', 'hihat', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01}},
         [_filt('bandpass', 10000, 1.4)], _on((i for i in range(_STEPS) if i % 4 != 0), 'C4'), pan=-0.2),
]

# ---------------------------------------------------------------------------
# PERCS — the small psy ear-candy: a laser zap into the next bar, phrase-end
# tom runs, FM bleeps bouncing in delay. Optional.
# ---------------------------------------------------------------------------
_PERCS = [
    # Laser zap — a membrane swept down over 0.2s, once per bar
    _cfg('zap', 'perc', -18, '8n', 'MembraneSynth',
         {'pitchDecay': 0.2, 'octaves': 5,
          'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.05}},
         [_pingpong('8n.', 0.4, 0.3)],
         _on([14, 30], 'G4')),
    # Tom run closing bar 2
    _cfg('toms', 'perc', -14, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 3,
          'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.9, 0.15)],
         [_N]*25 + ['E3', _N, 'D3', _N, 'C3', 'A2', _N]),
    # FM bleeps on the last 16th of every other beat
    _cfg('bleep', 'perc', -20, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 10,
          'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.02},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.02}},
         [_delay('8n.', 0.4, 0.3)],
         _on([3, 11, 19, 27], 'E6'), pan=0.3),
]

# ---------------------------------------------------------------------------
# LEADS — squelchy acid lines and FM zaps running 16th sequences in A
# phrygian (flat second) or phrygian dominant / harmonic minor (the raised
# third or seventh). Root-heavy on purpose: key coherence detects each line's
# root as its most common note. Dotted-8th delay is the psy default.
# ---------------------------------------------------------------------------
# Resonant saw through a snappy filter envelope: the acid squelch.
_ACID = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 11, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.15, 'release': 0.05},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.1, 'release': 0.05,
                       'baseFrequency': 260, 'octaves': 3.8},
}
# High FM index collapsing within a few ms: the zap — a bright attack over a sine tail.
_ZAP = {
    'harmonicity': 3, 'modulationIndex': 28,
    'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.04},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.02},
}
# Square into a resonant filter: hollower squelch, sits above the acid saw.
_SQUELCH_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'Q': 8, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.09, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.07, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 400, 'octaves': 3},
}

_LEADS = [
    # Acid 16th riff — root pedal with octave and flat-second stabs
    _cfg('lead', 'lead', -15, '16n', 'MonoSynth', _ACID,
         [_filt('lowpass', 1500, 2), _delay('8n.', 0.3, 0.2), _reverb(1.4, 0.18)],
         ['A3','A3','A4','A3','Bb3','A3','C4','A3','A3','A3','A4','A3','G3','A3','Bb3','A3',
          'A3','A3','A4','A3','Bb3','A3','C4','A3','D4','C4','Bb3','A3','G3','A3','Bb3','C4'],
         automation=[_auto('effect:0:frequency', 600, 4500, 'tri')]),
    # FM zaps on the back half of each beat, answered by a falling run
    _cfg('lead', 'lead', -13, '16n', 'FMSynth', _ZAP,
         [_delay('8n.', 0.35, 0.22), _reverb(1.6, 0.2)],
         [_N,_N,'A4','A5',_N,_N,'A4','Bb4',_N,_N,'A4','A5',_N,'G4','A4','C5',
          _N,_N,'A4','A5',_N,_N,'A4','Bb4',_N,_N,'A4','E5','F5','E5','D5','Bb4']),
    # Pedal riff — the root alternating with a falling phrygian line
    _cfg('lead', 'lead', -15, '16n', 'MonoSynth', _SQUELCH_SQUARE,
         [_filt('lowpass', 2200, 3), _delay('8n.', 0.28, 0.18)],
         ['A4','A4','E5','A4','F5','A4','E5','A4','A4','A4','E5','A4','Bb4','A4','C5','A4',
          'A4','A4','E5','A4','F5','A4','E5','A4','G5','F5','E5','D5','C5','Bb4','A4','Bb4'],
         automation=[_auto('effect:0:frequency', 900, 5000, 'tri')]),
    # Phrygian-dominant riff — the raised third gives the "eastern" colour
    _cfg('lead', 'lead', -14, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 10,
          'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0.1, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.05, 'release': 0.05}},
         [_delay('8n.', 0.32, 0.22), _reverb(1.8, 0.22)],
         ['A4','Bb4','C#5','Bb4','A4',_N,'E5',_N,'F5','E5','C#5','Bb4','A4',_N,_N,_N,
          'A4','Bb4','C#5','D5','E5',_N,'F5','E5','D5','C#5','Bb4','C#5','A4',_N,'A4',_N]),
    # Call and response — a low squelch question, answered an octave up
    _cfg('lead', 'lead', -15, '16n', 'MonoSynth', _ACID,
         [_filt('lowpass', 1800, 2), _delay('8n.', 0.35, 0.22), _reverb(1.5, 0.2)],
         ['A3',_N,'A3','C4',_N,'A3','Bb3',_N,'A3',_N,'A3','G3',_N,'A3',_N,_N,
          'A4',_N,'A4','C5',_N,'A4','D5',_N,'C5','Bb4','A4','G4','A4',_N,_N,_N],
         automation=[_auto('effect:0:frequency', 700, 4200, 'tri')]),
    # Gated acid — "x.xx" per beat, filter opening across both bars
    _cfg('lead', 'lead', -15, '16n', 'MonoSynth', _ACID,
         [_filt('lowpass', 1200, 3), _delay('16n', 0.25, 0.15), _reverb(1.2, 0.15)],
         ['A3',_N,'A3','A4','A3',_N,'Bb3','A3','A3',_N,'A3','A4','C4',_N,'Bb3','A3',
          'A3',_N,'A3','A4','A3',_N,'Bb3','A3','D4',_N,'C4','Bb3','A3',_N,'G3','Bb3'],
         automation=[_auto('effect:0:frequency', 500, 5000, 'ramp')]),
    # Zap arpeggio — root pedal under a minor / flat-two broken chord
    _cfg('lead', 'lead', -14, '16n', 'FMSynth', _ZAP,
         [_delay('8n.', 0.3, 0.2), _reverb(1.6, 0.2)],
         ['A4','E5','A4','C5','A4','E5','A4','A5','A4','F5','A4','D5','A4','F5','A4','Bb5',
          'A4','E5','A4','C5','A4','E5','A4','A5','A4','G5','A4','E5','A4','F5','E5','D5'],
         pan=0.12),
]

# ---------------------------------------------------------------------------
# PADS — optional, low and dark: lowpassed and quiet, entering after the
# groove is established. Nothing below the bass register.
# ---------------------------------------------------------------------------
_PADS = [
    # Dark open fifth, held a bar at a time
    _cfg('pad', 'pad', -21, '1m', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.8, 'release': 2.0}},
         [_filt('lowpass', 900, 1), _reverb(4.0, 0.5)],
         _on([0, 16], 'A2,E3'),
         entry_loop=2),
    # Phrygian swap — minor chord to the flat-two chord, filter breathing
    _cfg('pad', 'pad', -23, '1m', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.7, 'release': 2.0}},
         [_filt('lowpass', 700, 1), _chorus(0.5, 3, 0.4, 0.3), _reverb(4.5, 0.55)],
         ['A2,C3,E3'] + [_N]*15 + ['Bb2,D3,F3'] + [_N]*15,
         automation=[_auto('effect:0:frequency', 500, 1400, 'tri')],
         entry_loop=2),
    # AM drone — root to flat seven
    _cfg('pad', 'pad', -20, '1m', 'AMSynth',
         {'harmonicity': 1.0,
          'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.8, 'release': 1.5}},
         [_filt('lowpass', 1200, 1), _reverb(4.0, 0.6)],
         ['A3'] + [_N]*15 + ['G3'] + [_N]*15,
         entry_loop=2),
]

# ---------------------------------------------------------------------------
# FILLS — phrase-level accents (uplifters, swells, snare rolls) every 8-16 bars.
# ---------------------------------------------------------------------------
_FILLS = [
    # White-noise uplifter into the next phrase — every 16 bars
    _cfg('fill_uplifter', 'perc', -12, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.8, 'decay': 0.05, 'sustain': 0.95, 'release': 0.1}},
         [_reverb(1.0, 0.45), _filt('highpass', 1800, 1.3)],
         ['C3'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=7),
    # Reverse-cymbal style swell into bar 2 — every 8 bars
    _cfg('fill_swell', 'perc', -15, '2n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.9, 'decay': 0.05, 'sustain': 1, 'release': 0.3}},
         [_filt('highpass', 4000, 1), _reverb(2.0, 0.55)],
         [_N]*8 + ['C4'] + [_N]*23,
         loop_modulo=4, loop_modulo_remainder=3),
    # 16th snare roll on the final beat — every 16 bars
    _cfg('fill_roll', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.04}},
         [_reverb(0.6, 0.4), _filt('highpass', 1200, 1.5)],
         [_N]*28 + ['C3', 'C3', 'C3', 'C3'],
         loop_modulo=8, loop_modulo_remainder=7),
]


class PsytranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSYTRANCE
    BPM_RANGE = (143, 148)
    LEVEL_DB = 0.0
    KEY_ROLES = ('bass',)
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.2

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass['pattern']['velocities'] = _vel_roll(bass['pattern']['steps'], _ROLL_LEVELS, (0.85, 0.9))
        open_hat['pattern']['velocities'] = _vel_flat(open_hat['pattern']['steps'], 0.7, 0.88)

        layers = [kick, bass, open_hat]

        if random.random() < 0.85:
            closed_hat = copy.deepcopy(cls._pick(_CLOSED_HATS))
            closed_hat['pattern']['velocities'] = _vel_groove(closed_hat['pattern']['steps'])
            layers.append(closed_hat)

        # Some loops are just drums and the roll — the cue the learner most needs to hear bare.
        if random.random() < 0.85:
            lead = copy.deepcopy(cls._pick(_LEADS))
            steps = lead['pattern']['steps']
            lead['pattern']['velocities'] = _vel(steps, accent_prob=0.25, ghost_prob=0.06)
            if lead['instrument']['type'] == 'MonoSynth':
                lead['pattern']['slides'] = _slides(steps, 0.2)
            if random.random() < 0.4:
                lead['entry_loop'] = random.choice([2, 4])
            layers.append(lead)

        if random.random() < 0.4:
            perc = copy.deepcopy(cls._pick(_PERCS))
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.2, ghost_prob=0.1)
            layers.append(perc)

        if random.random() < 0.35:
            layers.append(copy.deepcopy(cls._pick(_PADS)))

        if random.random() < 0.5:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        cls._apply_key_coherence(layers)
        return layers

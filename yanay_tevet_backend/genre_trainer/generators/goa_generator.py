import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _reverb, _delay, _dist, _chorus, _filt, _pingpong, _auto, _vel,
    _vel_groove, _slides, _on, _vel_flat, _rolling, _vel_roll,
)

_STEPS = 32


# Inside each beat the 16th after the kick sits back under the kick's longer tail, the middle one
# leads. Slightly wider than full-on — the older rolls breathe a little more.
_ROLL_LEVELS = {1: (0.76, 0.84), 2: (0.88, 0.96), 3: (0.82, 0.9)}


# ---------------------------------------------------------------------------
# KICKS — strict four-on-the-floor, softer and longer than full-on: a slower
# pitch drop and a rounder body, the bouncier mid-'90s thump. Never distorted.
# ---------------------------------------------------------------------------
_KICKS = [
    # Classic '90s
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0, 'release': 0.1}},
         [], _on(range(0, _STEPS, 4), 'G1')),
    # Bouncy — longest body
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0, 'release': 0.1}},
         [], _on(range(0, _STEPS, 4), 'F#1')),
    # Room — a little space around it
    _cfg('kick', 'kick', -3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 6.5,
          'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.0, 0.1)], _on(range(0, _STEPS, 4), 'G1')),
    # Soft and round — lowpassed
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0, 'release': 0.1}},
         [_filt('lowpass', 1600, 0.7)], _on(range(0, _STEPS, 4), 'F1')),
    # Punchier late-'90s
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0, 'release': 0.09}},
         [], _on(range(0, _STEPS, 4), 'A1')),
    # Triangle body — warmer top end
    _cfg('kick', 'kick', -3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 7, 'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0, 'release': 0.1}},
         [_filt('lowpass', 2200, 0.7)], _on(range(0, _STEPS, 4), 'G1')),
]

# ---------------------------------------------------------------------------
# BASSES — rolling K-B-B-B like full-on, but warmer and older-sounding: saw
# (or detuned saw / square) MonoSynth through a gentle resonant lowpass, very
# little drive. Rolls with octave jumps and phrygian-dominant turns are the
# Goa flavour. Written on A1.
# ---------------------------------------------------------------------------
_MONO_GOA = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 2.5, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0, 'release': 0.05,
                       'baseFrequency': 160, 'octaves': 3.2},
}
# Two slightly detuned saws: the analogue warmth of the old hardware.
_FAT_GOA = {
    'oscillator': {'type': 'fatsawtooth', 'count': 2, 'spread': 14},
    'filter': {'Q': 2, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0, 'release': 0.05,
                       'baseFrequency': 150, 'octaves': 3},
}
_SQUARE_GOA = {
    'oscillator': {'type': 'square'},
    'filter': {'Q': 3, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.09, 'sustain': 0, 'release': 0.05,
                       'baseFrequency': 140, 'octaves': 3.4},
}

_BASSES = [
    # Pure roll
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_filt('lowpass', 900, 3), _dist(0.12, 0.15)],
         _rolling('A1'),
         automation=[_auto('effect:0:frequency', 400, 2200, 'tri')]),
    # Octave jump on the last 16th of every other beat
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _FAT_GOA,
         [_filt('lowpass', 850, 2.5)],
         _rolling('A1', {3: 'A2', 11: 'A2', 19: 'A2', 27: 'A2'}),
         automation=[_auto('effect:0:frequency', 380, 2000, 'tri')]),
    # Bouncing octave — the middle 16th of every beat an octave up
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth', _MONO_GOA,
         [_filt('lowpass', 950, 3)],
         _rolling('A1', {i: 'A2' for i in range(2, _STEPS, 4)}),
         automation=[_auto('effect:0:frequency', 420, 2400, 'tri')]),
    # Phrygian-dominant walk-down into the downbeat
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SQUARE_GOA,
         [_filt('lowpass', 800, 3), _dist(0.1, 0.12)],
         _rolling('A1', {29: 'D2', 30: 'C#2', 31: 'Bb1'}),
         automation=[_auto('effect:0:frequency', 380, 2100, 'tri')]),
    # Following the chords — up to the third, down to the flat seven
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_filt('lowpass', 900, 3)],
         _rolling('A1', {21: 'C2', 22: 'C2', 23: 'C2', 29: 'G1', 30: 'G1', 31: 'G1'}),
         automation=[_auto('effect:0:frequency', 400, 2300, 'ramp')]),
    # Low fifth, then a breath before the downbeat
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _FAT_GOA,
         [_filt('lowpass', 880, 2.5)],
         _rolling('A1', {25: 'E1', 26: 'E1', 27: 'E1', 31: _N}),
         automation=[_auto('effect:0:frequency', 380, 2000, 'tri')]),
    # Flat-two rub at the end of each bar
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SQUARE_GOA,
         [_filt('lowpass', 820, 3)],
         _rolling('A1', {13: 'Bb1', 29: 'Bb1', 30: 'Bb1'}),
         automation=[_auto('effect:0:frequency', 400, 2200, 'tri')]),
]

# ---------------------------------------------------------------------------
# HATS — the open hat on every offbeat plus 16th ticks; a shaker sometimes on top.
# ---------------------------------------------------------------------------
_OFFBEATS = range(2, _STEPS, 4)

_OPEN_HATS = [
    # Crisp '90s open hat
    _cfg('open_hat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 7000, 0.9)], _on(_OFFBEATS, 'C4')),
    # Ringing — resonant highpass for a metallic edge
    _cfg('open_hat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.11, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 7800, 4)], _on(_OFFBEATS, 'C4')),
    # Long sizzle with room
    _cfg('open_hat', 'hihat', -17, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0, 'release': 0.06}},
         [_filt('highpass', 8500, 0.8), _reverb(1.2, 0.18)], _on(_OFFBEATS, 'C4')),
    # Pink and soft
    _cfg('open_hat', 'hihat', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_filt('bandpass', 8000, 1.1)], _on(_OFFBEATS, 'C4')),
    # FM metal
    _cfg('open_hat', 'hihat', -19, '16n', 'FMSynth',
         {'harmonicity': 5.1, 'modulationIndex': 38,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.04},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 6000, 1)], _on(_OFFBEATS, 'A5')),
]

_CLOSED_HATS = [
    # Straight 16ths
    _cfg('closed_hat', 'hihat', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.028, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 9000, 0.8)], _on(range(_STEPS), 'C4'), pan=-0.2),
    # Around the open hat
    _cfg('closed_hat', 'hihat', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 8800, 1)], _on((i for i in range(_STEPS) if i % 4 != 2), 'C4'), pan=-0.2),
    # Off-16th ticks
    _cfg('closed_hat', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.022, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 9800, 1)], _on(range(1, _STEPS, 2), 'C4'), pan=-0.25),
    # FM tick 16ths
    _cfg('closed_hat', 'hihat', -25, '16n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 20,
          'envelope': {'attack': 0.001, 'decay': 0.022, 'sustain': 0, 'release': 0.01},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.022, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 7000, 1)], _on(range(_STEPS), 'C7'), pan=-0.15),
    # Off the kick
    _cfg('closed_hat', 'hihat', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01}},
         [_filt('bandpass', 9500, 1.4)], _on((i for i in range(_STEPS) if i % 4 != 0), 'C4'), pan=-0.2),
]

_SHAKERS = [
    _cfg('shaker', 'perc', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.008, 'decay': 0.045, 'sustain': 0, 'release': 0.02}},
         [_filt('bandpass', 6000, 1.2)], _on(range(_STEPS), 'C4'), pan=0.3),
    _cfg('shaker', 'perc', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.006, 'decay': 0.05, 'sustain': 0, 'release': 0.02}},
         [_filt('bandpass', 5200, 1.2)], _on((i for i in range(_STEPS) if i % 2 == 1), 'C4'), pan=0.3),
    _cfg('shaker', 'perc', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.01, 'decay': 0.06, 'sustain': 0, 'release': 0.02}},
         [_filt('bandpass', 7000, 1.5), _reverb(0.8, 0.12)], _on((i for i in range(_STEPS) if i % 4 != 0), 'C4'), pan=0.3),
]

# ---------------------------------------------------------------------------
# LEADS — the heart of Goa and the part to listen for: modal 16th lines in A
# phrygian, phrygian dominant (the raised third, the "eastern" sound) or
# harmonic minor, on squelchy resonant or detuned 90s voices drenched in
# dotted-8th delay and long reverb. Root-heavy so key coherence finds the
# right root; the filter on effect 0 opens and closes over the loop.
# ---------------------------------------------------------------------------
# Resonant saw with a filter envelope — the squelchy sequence voice.
_GOA_ACID = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 9, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0.25, 'release': 0.08},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0.15, 'release': 0.08,
                       'baseFrequency': 320, 'octaves': 3.5},
}
# Detuned saw stack — the wide mid-'90s lead.
_GOA_FATSAW = {
    'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 22},
    'envelope': {'attack': 0.004, 'decay': 0.2, 'sustain': 0.3, 'release': 0.15},
}
# Narrow pulse through a resonant filter: nasal and reed-like.
_GOA_REED = {
    'oscillator': {'type': 'pulse', 'width': 0.25},
    'filter': {'Q': 6, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.45, 'release': 0.12},
    'filterEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.4, 'release': 0.12,
                       'baseFrequency': 500, 'octaves': 2.5},
}
# FM bell — metallic and glassy, for answering phrases.
_GOA_BELL = {
    'harmonicity': 3.5, 'modulationIndex': 7,
    'envelope': {'attack': 0.002, 'decay': 0.3, 'sustain': 0.05, 'release': 0.3},
    'modulationEnvelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.1, 'release': 0.3},
}
# Pulse-width modulation — hollow and slowly moving.
_GOA_PWM = {
    'oscillator': {'type': 'pwm', 'modulationFrequency': 0.6},
    'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.35, 'release': 0.2},
}

_LEADS = [
    # Phrygian-dominant run — squelch up and down the scale
    _cfg('lead', 'lead', -13, '16n', 'MonoSynth', _GOA_ACID,
         [_filt('lowpass', 2600, 2.5), _delay('8n.', 0.4, 0.28), _reverb(3.5, 0.32, 0.02)],
         ['A4','Bb4','C#5','A4','D5','C#5','Bb4','A4','E5','A4','F5','E5','D5','C#5','Bb4','A4',
          'A4','Bb4','C#5','A4','D5','C#5','Bb4','A4','G5','F5','E5','F5','E5','D5','C#5','Bb4'],
         automation=[_auto('effect:0:frequency', 800, 5500, 'tri')]),
    # Pedal riff — the root alternating with a falling melody
    _cfg('lead', 'lead', -13, '16n', 'MonoSynth', _GOA_REED,
         [_filt('lowpass', 3000, 2), _delay('8n.', 0.38, 0.26), _reverb(3.0, 0.3, 0.02)],
         ['A4','E5','A4','F5','A4','E5','A4','D5','A4','E5','A4','F5','A4','G5','F5','E5',
          'A4','E5','A4','F5','A4','E5','A4','C#5','A4','D5','A4','Bb4','A4','C#5','D5','E5'],
         automation=[_auto('effect:0:frequency', 900, 5000, 'tri')]),
    # Slow modal melody — long notes, the detuned stack in a big room
    _cfg('lead', 'lead', -14, '8n', 'Synth', _GOA_FATSAW,
         [_filt('lowpass', 2400, 1.5), _delay('8n.', 0.45, 0.3), _reverb(4.5, 0.4, 0.03)],
         ['A4',_N,_N,'Bb4',_N,_N,'C#5',_N,'D5',_N,'C#5',_N,'Bb4',_N,'A4',_N,
          'A4',_N,'A4','Bb4',_N,_N,'C#5',_N,'E5',_N,'F5',_N,'E5','D5','C#5','A4'],
         automation=[_auto('effect:0:frequency', 700, 4200, 'tri')]),
    # Low squelch sequence — 303-style, with slides
    _cfg('lead', 'lead', -14, '16n', 'MonoSynth', _GOA_ACID,
         [_filt('lowpass', 1800, 3), _delay('8n.', 0.35, 0.24), _reverb(3.0, 0.28, 0.02)],
         ['A3','A3','A4','A3','Bb3','A3','C#4','A3','A3','D4','A3','E4','F4','E4','C#4','Bb3',
          'A3','A3','A4','A3','Bb3','A3','C#4','A3','A3','G3','A3','Bb3','A3','C#4','D4','E4'],
         automation=[_auto('effect:0:frequency', 600, 4800, 'ramp')]),
    # Harmonic-minor climb — the raised seventh pulling back to the root
    _cfg('lead', 'lead', -14, '16n', 'Synth', _GOA_PWM,
         [_filt('lowpass', 2800, 2), _delay('8n.', 0.4, 0.28), _reverb(3.5, 0.35, 0.02)],
         ['A4','B4','C5','A4','E5','C5','B4','A4','G#4','A4','B4','C5','E5','D5','C5','B4',
          'A4','B4','C5','A4','F5','E5','D5','C5','A4','C5','D5','E5','G#5','E5','B4','A4'],
         automation=[_auto('effect:0:frequency', 800, 5200, 'tri')]),
    # Broken-chord lead — minor to flat-two, the root returning between
    _cfg('lead', 'lead', -14, '16n', 'Synth', _GOA_FATSAW,
         [_filt('lowpass', 2600, 2), _delay('8n.', 0.42, 0.28), _reverb(4.0, 0.35, 0.02)],
         ['A4','C5','E5','A5','E5','C5','A4','A4','Bb4','D5','F5','Bb5','F5','D5','Bb4','D5',
          'A4','C5','E5','A5','E5','C5','A4','A4','G4','Bb4','D5','G5','F5','E5','D5','C5'],
         automation=[_auto('effect:0:frequency', 900, 5000, 'tri')]),
    # Slow pedal melody — reed voice in 8ths around the root
    _cfg('lead', 'lead', -13, '8n', 'MonoSynth', _GOA_REED,
         [_filt('lowpass', 2800, 2), _delay('8n.', 0.45, 0.3), _reverb(4.0, 0.38, 0.03)],
         ['A4',_N,'A4','Bb4','A4',_N,'G4',_N,'A4',_N,'C5',_N,'Bb4',_N,'A4',_N,
          'A4',_N,'A4','Bb4','A4',_N,'G4',_N,'F4',_N,'G4',_N,'Bb4',_N,'A4','G4'],
         automation=[_auto('effect:0:frequency', 900, 4500, 'tri')]),
]

# ---------------------------------------------------------------------------
# CALL AND RESPONSE — two leads trading bars: the call phrases in bar 1, a
# second voice answers in bar 2 from the other side of the stereo field.
# Pairs are fixed so the answer always shares the call's scale.
# ---------------------------------------------------------------------------
_BAR_REST = [_N] * 16

_CALL_RESPONSES = [
    # Phrygian-dominant question, bell answer an octave up
    (_cfg('call', 'lead', -13, '16n', 'MonoSynth', _GOA_ACID,
          [_filt('lowpass', 2400, 2.5), _delay('8n.', 0.4, 0.26), _reverb(3.5, 0.32, 0.02)],
          ['A4',_N,'Bb4','A4',_N,'C#5',_N,'D5','E5',_N,'D5','C#5','Bb4',_N,'A4',_N] + _BAR_REST,
          automation=[_auto('effect:0:frequency', 900, 5000, 'tri')], pan=-0.35),
     _cfg('response', 'lead', -15, '16n', 'FMSynth', _GOA_BELL,
          [_pingpong('8n.', 0.4, 0.3), _reverb(4.0, 0.4, 0.03)],
          _BAR_REST + ['A5',_N,'A5','G5',_N,'F5',_N,'E5','F5',_N,'E5','D5','C#5',_N,'A4',_N],
          pan=0.35)),
    # Slow reed phrase, echoed higher by the PWM voice
    (_cfg('call', 'lead', -13, '16n', 'MonoSynth', _GOA_REED,
          [_filt('lowpass', 2800, 2), _delay('8n.', 0.42, 0.28), _reverb(4.0, 0.36, 0.03)],
          ['A4',_N,_N,_N,'Bb4',_N,'A4',_N,'G4',_N,'F4',_N,'G4',_N,'A4',_N] + _BAR_REST,
          automation=[_auto('effect:0:frequency', 900, 4200, 'tri')], pan=-0.35),
     _cfg('response', 'lead', -15, '16n', 'Synth', _GOA_PWM,
          [_pingpong('8n.', 0.42, 0.3), _reverb(4.0, 0.38, 0.03)],
          _BAR_REST + ['A5',_N,'Bb5',_N,'A5',_N,'G5',_N,'F5',_N,'E5',_N,'F5',_N,'A5',_N],
          pan=0.35)),
    # Fast minor / flat-two burst, answered by a descending bell figure
    (_cfg('call', 'lead', -14, '16n', 'Synth', _GOA_FATSAW,
          [_filt('lowpass', 2600, 2), _delay('8n.', 0.4, 0.28), _reverb(3.5, 0.35, 0.02)],
          ['A4','C5','E5','A4','D5','C5','Bb4','A4','Bb4','C5','A4',_N,_N,_N,_N,_N] + _BAR_REST,
          automation=[_auto('effect:0:frequency', 800, 4800, 'tri')], pan=-0.35),
     _cfg('response', 'lead', -15, '16n', 'FMSynth', _GOA_BELL,
          [_pingpong('8n.', 0.4, 0.3), _reverb(4.0, 0.4, 0.03)],
          _BAR_REST + ['A5','G5','F5','A5','E5','F5','D5','A5','C5','D5','A5',_N,_N,_N,_N,_N],
          pan=0.35)),
    # Low squelch question, reed answer
    (_cfg('call', 'lead', -14, '16n', 'MonoSynth', _GOA_ACID,
          [_filt('lowpass', 1800, 3), _delay('8n.', 0.38, 0.26), _reverb(3.0, 0.3, 0.02)],
          ['A3','A3','Bb3','A3','C#4','A3','D4','A3','E4','D4','C#4','Bb3','A3',_N,_N,_N] + _BAR_REST,
          automation=[_auto('effect:0:frequency', 600, 4200, 'tri')], pan=-0.35),
     _cfg('response', 'lead', -14, '16n', 'MonoSynth', _GOA_REED,
          [_filt('lowpass', 3000, 2), _pingpong('8n.', 0.4, 0.3), _reverb(3.5, 0.35, 0.02)],
          _BAR_REST + ['A4',_N,'E5',_N,'D5',_N,'C#5','D5','A4',_N,'Bb4',_N,'A4',_N,_N,_N],
          automation=[_auto('effect:0:frequency', 1000, 4500, 'tri')], pan=0.35)),
]

# ---------------------------------------------------------------------------
# ARPS — quieter, high-register 16th arpeggios layered over the lead: root
# pedals, 3-against-4 cycles and broken chords, all in the lead's modes.
# ---------------------------------------------------------------------------
_ARPS = [
    # Root-pedal arp in phrygian dominant
    _cfg('arp', 'lead', -17, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.08, 'release': 0.15}},
         [_delay('16n', 0.3, 0.2), _reverb(3.0, 0.45)],
         ['A5','E6','A5','C#6','A5','D6','A5','Bb5','A5','E6','A5','C#6','A5','F6','A5','E6',
          'A5','E6','A5','C#6','A5','D6','A5','Bb5','A5','G6','A5','F6','A5','E6','D6','C#6'],
         pan=0.25),
    # Three-note cycle against the 4/4 — the pattern lands somewhere new on every beat
    _cfg('arp', 'lead', -18, '16n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0.1, 'release': 0.2}},
         [_delay('8n.', 0.35, 0.25), _reverb(3.5, 0.5)],
         [('A5', 'E6', 'A6')[i % 3] for i in range(_STEPS)],
         pan=0.25),
    # Broken chords — root, third, fifth, octave over minor and flat-two
    _cfg('arp', 'lead', -19, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'filter': {'Q': 4, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.08},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.05,
                             'baseFrequency': 900, 'octaves': 2.5}},
         [_delay('16n', 0.3, 0.2), _reverb(3.0, 0.45)],
         ['A5','C#6','E6','A6','A5','C#6','E6','A6','Bb5','D6','F6','Bb6','A5','C#6','E6','A6',
          'A5','C#6','E6','A6','A5','C#6','E6','A6','G5','Bb5','D6','G6','A5','C#6','E6','A6'],
         pan=0.25),
    # FM bell arp in 8ths
    _cfg('arp', 'lead', -18, '16n', 'FMSynth', _GOA_BELL,
         [_pingpong('8n.', 0.4, 0.3), _reverb(4.0, 0.5)],
         ['A5',_N,'E6',_N,'A6',_N,'E6',_N,'F6',_N,'E6',_N,'C#6',_N,'A5',_N,
          'A5',_N,'E6',_N,'A6',_N,'G6',_N,'F6',_N,'E6',_N,'D6',_N,'A5',_N],
         pan=0.25),
    # Descending cascade
    _cfg('arp', 'lead', -18, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.05, 'release': 0.15}},
         [_delay('8n.', 0.38, 0.25), _reverb(3.5, 0.5)],
         ['A6','E6','C6','A5','E6','C6','A5','E5','A6','E6','C6','A5','F6','D6','Bb5','A5',
          'A6','E6','C6','A5','E6','C6','A5','E5','A6','F6','D6','A5','G6','E6','C6','A5'],
         pan=0.25),
]

# ---------------------------------------------------------------------------
# PADS — long cosmic pads under the leads, entering after the intro.
# ---------------------------------------------------------------------------
_PADS = [
    # Minor to flat-two — the phrygian lift
    _cfg('pad', 'pad', -20, '1m', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.7, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5}},
         [_filt('lowpass', 1400, 1), _chorus(0.4, 4, 0.5, 0.35), _reverb(5.0, 0.6)],
         ['A3,C4,E4'] + [_N]*15 + ['Bb3,D4,F4'] + [_N]*15,
         automation=[_auto('effect:0:frequency', 800, 2200, 'tri')],
         entry_loop=2),
    # AM pad — root to flat seven
    _cfg('pad', 'pad', -19, '1m', 'AMSynth',
         {'harmonicity': 0.8,
          'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5},
          'modulationEnvelope': {'attack': 0.7, 'decay': 0.3, 'sustain': 0.7, 'release': 2.0}},
         [_reverb(5.0, 0.7)],
         ['A3'] + [_N]*15 + ['G3'] + [_N]*15,
         entry_loop=2),
    # Phrygian-dominant major chord — bright and "eastern"
    _cfg('pad', 'pad', -21, '1m', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.9, 'release': 3.0}},
         [_chorus(0.4, 4, 0.5, 0.3), _reverb(6.0, 0.75)],
         _on([0, 16], 'A3,C#4,E4'),
         entry_loop=2),
]

# ---------------------------------------------------------------------------
# FX — sci-fi ear candy: laser zaps, bubbling FM blips, a noise riser.
# ---------------------------------------------------------------------------
_FX = [
    # Laser zap into bar 2, every other loop
    _cfg('zap', 'perc', -17, '8n', 'MembraneSynth',
         {'pitchDecay': 0.25, 'octaves': 5,
          'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0, 'release': 0.05}},
         [_pingpong('8n.', 0.45, 0.35), _reverb(2.5, 0.3)],
         _on([14], 'G4'),
         loop_modulo=2, loop_modulo_remainder=1),
    # Bubbling FM blips
    _cfg('bubbles', 'perc', -21, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 12,
          'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.02}},
         [_pingpong('16n', 0.35, 0.3)],
         [_N,_N,_N,'E6',_N,_N,_N,_N,_N,_N,_N,'G6',_N,_N,_N,_N,
          _N,_N,_N,'E6',_N,_N,_N,_N,_N,_N,'C6',_N,'D6',_N,_N,_N], pan=-0.3),
    # Noise riser into the next phrase — every 8 loops
    _cfg('riser', 'perc', -14, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.8, 'decay': 0.05, 'sustain': 0.95, 'release': 0.1}},
         [_filt('highpass', 1800, 1.3), _reverb(1.5, 0.45)],
         ['C3'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=7),
]


class GoaTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.GOA
    BPM_RANGE = (138, 145)
    LEVEL_DB = -2.5
    PROFILE = GenreProfile(
        drums='Softer, longer four-on-the-floor kick; offbeat hat and 16ths',
        bass='Warm rolling K-B-B-B, often jumping octaves',
        signature='Layered melodic leads and arpeggios in Eastern-sounding modes, often in call and response',
        mood='Mystical, uplifting, drenched in delay',
        key_trait='signature',
        kick_pattern='four',
        bass_pattern='rolling',
    )
    KEY_ROLES = ('lead', 'bass')
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.25

    @classmethod
    def _lead_velocities(cls, lead: dict[str, Any]) -> None:
        steps = lead['pattern']['steps']
        lead['pattern']['velocities'] = _vel(steps, accent_prob=0.22, ghost_prob=0.06)
        if lead['instrument']['type'] == 'MonoSynth':
            lead['pattern']['slides'] = _slides(steps, 0.2)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))

        kick['pattern']['velocities'] = _vel_flat(kick['pattern']['steps'], 0.9, 1.0)
        bass['pattern']['velocities'] = _vel_roll(bass['pattern']['steps'], _ROLL_LEVELS, (0.82, 0.88))
        open_hat['pattern']['velocities'] = _vel_flat(open_hat['pattern']['steps'], 0.68, 0.86)

        layers = [kick, bass, open_hat]

        if random.random() < 0.75:
            closed_hat = copy.deepcopy(cls._pick(_CLOSED_HATS))
            closed_hat['pattern']['velocities'] = _vel_groove(closed_hat['pattern']['steps'])
            layers.append(closed_hat)

        if random.random() < 0.35:
            shaker = copy.deepcopy(cls._pick(_SHAKERS))
            shaker['pattern']['velocities'] = _vel_groove(shaker['pattern']['steps'])
            layers.append(shaker)

        # The lead is always there — it is what makes it Goa. Either one long line or two voices
        # trading bars.
        if random.random() < 0.4:
            call, response = copy.deepcopy(random.choice(_CALL_RESPONSES))
            cls._lead_velocities(call)
            cls._lead_velocities(response)
            layers += [call, response]
        else:
            lead = copy.deepcopy(cls._pick(_LEADS))
            cls._lead_velocities(lead)
            layers.append(lead)

        if random.random() < 0.55:
            arp = copy.deepcopy(cls._pick(_ARPS))
            arp['pattern']['velocities'] = _vel(arp['pattern']['steps'], accent_prob=0.18, ghost_prob=0.1)
            arp['entry_loop'] = random.choice([0, 2])
            layers.append(arp)

        if random.random() < 0.45:
            layers.append(copy.deepcopy(cls._pick(_PADS)))

        if random.random() < 0.4:
            fx = copy.deepcopy(cls._pick(_FX))
            fx['pattern']['velocities'] = _vel(fx['pattern']['steps'], accent_prob=0.15, ghost_prob=0.1)
            layers.append(fx)

        cls._apply_key_coherence(layers)
        return layers

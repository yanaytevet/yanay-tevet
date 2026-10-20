import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _chorus, _delay, _dist, _filt, _reverb, _vel, _vel_groove,
    _vel_kick, _vel_snare, _on, _at,
)


_QUARTERS = list(range(0, 32, 4))
_OFFBEATS = list(range(2, 32, 4))

# ---------------------------------------------------------------------------
# KICKS — four-on-the-floor, nothing else: the kick on every quarter is the
# floor the whole groove swings over. Variety is in the sound only — round,
# warm membranes with a soft click (the 'deep' kick profile).
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.2}},
         [], _on(_QUARTERS, 'C1')),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 5.5, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.3}},
         [], _on(_QUARTERS, 'C1')),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.0}},
         [], _on(_QUARTERS, 'D1')),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 5, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.4}},
         [], _on(_QUARTERS, 'B0')),
    # Slightly saturated — the warmer, analogue-drum-machine kick
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.12, 0.2)], _on(_QUARTERS, 'C1')),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 6.5, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.1}},
         [], _on(_QUARTERS, 'C#1')),
]

# ---------------------------------------------------------------------------
# CLAPS — clap or snare on 2 and 4 (steps 4, 12, 20, 28), always. Some add a
# single swung ghost clap; the reverb tail is what makes it sound like a room.
# ---------------------------------------------------------------------------
_CLAPS = [
    # . . . . C . . . . . . . C . . . | same
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.14, 'sustain': 0, 'release': 0.08}},
         [_filt('bandpass', 1400, 0.9), _reverb(1.0, 0.35)],
         _on([4, 12, 20, 28])),
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.004, 'decay': 0.16, 'sustain': 0, 'release': 0.09}},
         [_filt('bandpass', 1700, 0.8), _reverb(1.3, 0.4)],
         _on([4, 12, 20, 28])),
    # Ghost clap on the "a" of 4 at the end of the loop
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0, 'release': 0.08}},
         [_filt('bandpass', 1300, 0.9), _reverb(1.2, 0.38)],
         _on([4, 12, 20, 28, 31])),
    # Snare instead of clap — the tighter, garage-leaning backbeat
    _cfg('clap', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 1200, 0.7), _reverb(0.9, 0.3)],
         _on([4, 12, 20, 28])),
    # Ghost on the "e" of 2 in bar 2
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.006, 'decay': 0.17, 'sustain': 0, 'release': 0.1}},
         [_filt('bandpass', 1500, 0.8), _reverb(1.5, 0.42)],
         _on([4, 12, 20, 21, 28])),
    # Long, roomy clap
    _cfg('clap', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0, 'release': 0.12}},
         [_filt('bandpass', 1200, 0.7), _reverb(1.8, 0.45)],
         _on([4, 12, 20, 28])),
]

# ---------------------------------------------------------------------------
# OPEN HATS — the signature: an open hat on every offbeat 8th (the "and" of
# each beat, i % 4 == 2), the "tss" between kicks that every house track has.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    _cfg('open_hat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.22, 'release': 0.12},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 5500, 'octaves': 1.5},
         [], _on(_OFFBEATS, 'C4')),
    _cfg('open_hat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 440, 'envelope': {'attack': 0.001, 'decay': 0.28, 'release': 0.15},
          'harmonicity': 5.4, 'modulationIndex': 30, 'resonance': 6200, 'octaves': 1.4},
         [], _on(_OFFBEATS, 'C4')),
    # Shorter, brighter — the 909 open hat
    _cfg('open_hat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 480, 'envelope': {'attack': 0.001, 'decay': 0.16, 'release': 0.1},
          'harmonicity': 5.8, 'modulationIndex': 36, 'resonance': 7000, 'octaves': 1.6},
         [], _on(_OFFBEATS, 'C4')),
    # Darker, washier open hat with a touch of room
    _cfg('open_hat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 360, 'envelope': {'attack': 0.001, 'decay': 0.32, 'release': 0.18},
          'harmonicity': 5.1, 'modulationIndex': 28, 'resonance': 4800, 'octaves': 1.5},
         [_reverb(0.8, 0.15)], _on(_OFFBEATS, 'C4')),
    # Noise-based open hat — softer, more like a sampled loop
    _cfg('open_hat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0, 'release': 0.1}},
         [_filt('highpass', 7000, 0.7)], _on(_OFFBEATS, 'C4')),
]

# ---------------------------------------------------------------------------
# CLOSED HATS & SHAKERS — 16ths that the transport swing turns into the house
# shuffle. Quiet and short so the open hat stays the loudest top.
# ---------------------------------------------------------------------------
_CLOSED_HAT = {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015},
               'harmonicity': 5.4, 'modulationIndex': 34, 'resonance': 8000, 'octaves': 1.5}

_CLOSED_HATS = [
    # Full swung 16ths
    _cfg('closed_hat', 'hihat', -20, '16n', 'MetalSynth', _CLOSED_HAT, [],
         _on(list(range(32)), 'C4')),
    # 16ths that leave the offbeat to the open hat
    _cfg('closed_hat', 'hihat', -19, '16n', 'MetalSynth', _CLOSED_HAT, [],
         _on([i for i in range(32) if i % 4 != 2], 'C4')),
    # The "e" and "a" only — the swung tick that most defines the shuffle
    _cfg('closed_hat', 'hihat', -18, '16n', 'MetalSynth', _CLOSED_HAT, [],
         _on(list(range(1, 32, 2)), 'C4')),
    # Shaker 16ths
    _cfg('shaker', 'hihat', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.035, 'sustain': 0, 'release': 0.015}},
         [_filt('highpass', 5000, 0.7)], _on(list(range(32)), 'C4')),
    # Shaker on the "e" and "a" with the occasional "and" — a looser hand-played feel
    _cfg('shaker', 'hihat', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.04, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 6000, 0.7)],
         _on([1, 3, 5, 7, 9, 11, 13, 14, 15, 17, 19, 21, 23, 25, 27, 29, 30, 31], 'C4')),
    # On the beat and the "a", with an "e" every half bar — a skippy Chicago-style tick
    _cfg('closed_hat', 'hihat', -19, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012},
          'harmonicity': 5.8, 'modulationIndex': 38, 'resonance': 8500, 'octaves': 1.6},
         [], _on([0, 3, 4, 7, 8, 9, 11, 12, 15, 16, 19, 20, 23, 24, 25, 27, 28, 31], 'C4')),
]

# ---------------------------------------------------------------------------
# BASSES — never on the kick. House bass lives in the gaps: the offbeat 8th,
# the "a" and the "e" around it, with octave jumps for bounce. Short plucky
# notes so each one ends before the next kick. Every line puts its root first
# and most often, which key coherence locks to.
# ---------------------------------------------------------------------------
_PLUCK_SAW = {'oscillator': {'type': 'sawtooth'},
              'envelope': {'attack': 0.005, 'decay': 0.18, 'sustain': 0.3, 'release': 0.1},
              'filter': {'Q': 3, 'type': 'lowpass', 'rolloff': -24},
              'filterEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.15, 'release': 0.1,
                                 'baseFrequency': 180, 'octaves': 3}}

_BASSES = [
    # A minor — every offbeat, the root with an octave jump at the end of each bar
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _PLUCK_SAW, [],
         _at({2: 'A1', 6: 'A1', 10: 'A1', 14: 'A2', 18: 'A1', 22: 'A1', 26: 'G1', 30: 'A2'})),
    # C minor — the "and" plus an octave-up "a" in each beat, a bouncing disco-house shape
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.25, 'release': 0.08},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.2, 'release': 0.08,
                             'baseFrequency': 220, 'octaves': 2.5}},
         [],
         _at({2: 'C2', 3: 'C3', 7: 'C2', 10: 'C2', 11: 'C3', 14: 'Bb1',
              18: 'C2', 19: 'C3', 23: 'C2', 26: 'Eb2', 27: 'F2', 30: 'G1'})),
    # D minor deep-house sub — rounder, longer offbeat notes with a syncopated answer
    _cfg('bass', 'bass', -4, '8n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.5, 'release': 0.12}},
         [_filt('lowpass', 500, 1)],
         _at({2: 'D2', 10: 'D2', 13: 'F2', 18: 'D2', 26: 'C2', 29: 'A1'})),
    # G minor — octave bounce on every "and"-"a" pair, the FM warmth of a classic organ bass
    _cfg('bass', 'bass', -7, '16n', 'FMSynth',
         {'harmonicity': 1.0, 'modulationIndex': 2.5,
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.3, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.2, 'release': 0.08}},
         [_filt('lowpass', 900, 1)],
         _at({2: 'G1', 3: 'G2', 6: 'G1', 7: 'G2', 10: 'G1', 11: 'G2', 14: 'F2',
              18: 'G1', 19: 'G2', 22: 'G1', 23: 'G2', 26: 'Bb1', 27: 'Bb2', 30: 'D2'})),
    # F minor — a soulful walk up the chord on the offbeats
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.4, 'release': 0.12},
          'filterEnvelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.3, 'release': 0.12,
                             'baseFrequency': 160, 'octaves': 2.5}},
         [],
         _at({2: 'F1', 6: 'Ab1', 10: 'C2', 14: 'Eb2', 18: 'F1', 22: 'F1', 26: 'Db2', 30: 'C2'})),
    # B minor — the "a" of 1 and the "e" of 3: a syncopated line that swings against the kick
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _PLUCK_SAW, [],
         _at({3: 'B1', 6: 'B1', 9: 'D2', 14: 'B1', 19: 'B1', 22: 'B1', 25: 'A1', 30: 'F#1'})),
    # E minor — "and" plus "e"-of-the-next-beat pairs, a garage-tinged skip
    _cfg('bass', 'bass', -5, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.4, 'release': 0.1}},
         [_dist(0.2, 0.25)],
         _at({2: 'E2', 5: 'E2', 10: 'E2', 13: 'G2', 18: 'E2', 21: 'E2', 26: 'D2', 29: 'B1'})),
]

# ---------------------------------------------------------------------------
# CHORD STABS — organ and piano 7th/9th chords on offbeats and syncopations:
# the soulful harmony of house. Tonic chord first and most often, so key
# coherence lines it up with the bass root. Organs are custom partials
# (drawbar-like harmonics); pianos are bright partials with a fast decay.
# ---------------------------------------------------------------------------
_ORGAN = {'oscillator': {'type': 'custom', 'partials': [1, 0.8, 0.6, 0.5, 0, 0.35, 0, 0.25]},
          'envelope': {'attack': 0.004, 'decay': 0.2, 'sustain': 0.35, 'release': 0.12}}
_PIANO = {'oscillator': {'type': 'custom', 'partials': [1, 0.5, 0.3, 0.2, 0.12, 0.08]},
          'envelope': {'attack': 0.002, 'decay': 0.5, 'sustain': 0.05, 'release': 0.35}}

_AM9 = 'A3,C4,E4,G4,B4'
_DM9 = 'D3,F3,A3,C4,E4'
_AM7 = 'A3,C4,E4,G4'
_DM7 = 'D3,F3,A3,C4'
_CM9 = 'C3,Eb3,G3,Bb3,D4'
_FM9 = 'F3,Ab3,C4,Eb4,G4'
_EM7 = 'E3,G3,B3,D4'
_CMAJ7 = 'C3,E3,G3,B3'
_GM9 = 'G3,Bb3,D4,F4,A4'
_EBMAJ7 = 'Eb3,G3,Bb3,D4'

_STABS = [
    # Organ Am9 on every offbeat, moving to Dm9 at the end of each bar
    _cfg('organ_stab', 'stab', -15, '16n', 'PolySynth', _ORGAN,
         [_chorus(4, 2.5, 0.4, 0.35), _reverb(1.4, 0.3)],
         _at({2: _AM9, 6: _AM9, 10: _AM9, 14: _DM9, 18: _AM9, 22: _AM9, 26: _AM9, 30: _DM9})),
    # Piano Am7 / Dm7 on the "a" of 1 and the "and" of 2 — the classic syncopated house-piano push
    _cfg('piano_stab', 'stab', -14, '8n', 'PolySynth', _PIANO,
         [_reverb(1.6, 0.32), _delay('8n.', 0.2, 0.12)],
         _at({3: _AM7, 6: _AM7, 11: _AM7, 14: _AM7, 19: _AM7, 22: _AM7, 27: _DM7, 30: _DM7})),
    # Organ Cm9 / Fm9 held an 8th on the "and" of 2 and 4 — the deep, Chicago chord
    _cfg('organ_stab', 'stab', -16, '8n', 'PolySynth', _ORGAN,
         [_filt('lowpass', 2400, 0.8), _chorus(3, 3, 0.5, 0.35), _reverb(1.8, 0.35)],
         _at({6: _CM9, 14: _CM9, 22: _CM9, 30: _FM9})),
    # Piano Em7 -> Cmaj7 (i to bVI) in a dotted pattern (and, e-of-2, and, e-of-4)
    _cfg('piano_stab', 'stab', -14, '16n', 'PolySynth', _PIANO,
         [_reverb(1.4, 0.3), _filt('lowpass', 3200, 0.7)],
         _at({2: _EM7, 5: _EM7, 10: _EM7, 13: _EM7, 18: _EM7, 21: _EM7, 26: _CMAJ7, 29: _CMAJ7})),
    # Organ Gm9 / Ebmaj7 — sparse, on the "a" of 2 and the "and" of 3, delayed into the gaps
    _cfg('organ_stab', 'stab', -16, '16n', 'PolySynth', _ORGAN,
         [_delay('8n', 0.3, 0.2), _reverb(1.6, 0.3)],
         _at({7: _GM9, 10: _GM9, 23: _GM9, 26: _EBMAJ7})),
    # Piano Am9 / Dm9 stabs on the offbeats of beats 1 and 3 only, letting the hats breathe
    _cfg('piano_stab', 'stab', -14, '8n', 'PolySynth', _PIANO,
         [_chorus(0.8, 3, 0.3, 0.25), _reverb(2.0, 0.35)],
         _at({2: _AM9, 10: _AM9, 18: _AM9, 26: _DM9})),
]

# ---------------------------------------------------------------------------
# PADS — warm chord beds under the groove. Tonic chord first.
# ---------------------------------------------------------------------------
_PADS = [
    _cfg('chord_pad', 'pad', -22, '1n', 'PolySynth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 20},
          'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.7, 'release': 1.8}},
         [_filt('lowpass', 1200, 0.7), _chorus(0.5, 3, 0.4, 0.3), _reverb(3.0, 0.55)],
         _at({0: 'A2,E3,G3,C4', 16: 'F2,C3,E3,A3'})),
    _cfg('chord_pad', 'pad', -21, '1n', 'PolySynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}},
         [_chorus(0.4, 4, 0.5, 0.35), _reverb(3.5, 0.6)],
         _at({0: 'D3,F3,A3,C4', 16: 'D3,F3,A3,C4'})),
    _cfg('chord_pad', 'pad', -22, '2n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.7, 'release': 1.5},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.6, 'release': 1.2}},
         [_reverb(2.5, 0.6), _chorus(0.5, 3, 0.4, 0.3)],
         _at({0: 'A2', 8: 'E2', 16: 'A2', 24: 'C3'})),
    _cfg('chord_pad', 'pad', -22, '1n', 'PolySynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.7, 'decay': 0.5, 'sustain': 0.9, 'release': 2.5}},
         [_reverb(4.0, 0.7)],
         _at({0: 'G2,Bb2,D3,F3', 16: 'Eb2,G2,Bb2,D3'})),
]

# ---------------------------------------------------------------------------
# FILLS — phrase-level accents gated by loop_modulo.
# loop_modulo=4 fires every 8 bars; loop_modulo=8 fires every 16 bars.
# ---------------------------------------------------------------------------
_FILLS = [
    # White-noise riser across the last loop of a 16-bar phrase
    _cfg('fill_riser', 'perc', -14, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.6, 'decay': 0.05, 'sustain': 0.95, 'release': 0.15}},
         [_reverb(1.5, 0.5), _filt('highpass', 2000, 1.2)],
         _on([0], 'C3'),
         loop_modulo=8, loop_modulo_remainder=7),
    # Clap doubled on the last two 16ths, every 8 bars — drives into the next phrase
    _cfg('fill_clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.2, 0.55)],
         _on([30, 31]),
         loop_modulo=4, loop_modulo_remainder=3),
    # Swelling cymbal wash every 16 bars
    _cfg('fill_wash', 'perc', -16, '2n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 1.0, 'decay': 0.4, 'release': 0.8},
          'harmonicity': 3.5, 'modulationIndex': 18, 'resonance': 5000, 'octaves': 1.4},
         [_reverb(2.5, 0.6)],
         _on([16], 'C4'),
         loop_modulo=8, loop_modulo_remainder=7),
]

# ---------------------------------------------------------------------------
# PERCUSSION — optional hand percussion on syncopated 16ths, adding to the swing.
# ---------------------------------------------------------------------------
_PERCS = [
    # Conga on the "and" of 1 and the "e" of 3
    _cfg('conga', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.1}},
         [_reverb(0.4, 0.18)],
         _at({2: 'G3', 9: 'G3', 18: 'G3', 25: 'G3', 30: 'D4'})),
    # Rim click on syncopated 16ths
    _cfg('rim', 'perc', -17, '16n', 'MetalSynth',
         {'frequency': 1500, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 3.0, 'modulationIndex': 12, 'resonance': 4000, 'octaves': 1.0},
         [],
         _on([6, 14, 19, 22, 30], 'C4')),
    # Bongo pair answering the clap
    _cfg('bongo', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 1.5, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.5, 0.2)],
         _at({7: 'D4', 15: 'A4', 23: 'D4', 27: 'A4', 31: 'D4'}), pan=-0.35),
]


class HouseTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HOUSE
    BPM_RANGE = (122, 128)
    LEVEL_DB = -1.6
    SWING = 0.12  # The house shuffle on 16ths: swung closed hats against the straight open hat
    KEY_ROLES = ('hihat', 'stab')
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.75

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        clap = copy.deepcopy(cls._pick(_CLAPS))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))
        closed_hat = copy.deepcopy(cls._pick(_CLOSED_HATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
        # The open hat is the loudest top and stays even; accents come from the swung 16ths under it.
        open_hat['pattern']['velocities'] = [_N if s is None else round(random.uniform(0.75, 0.9), 2)
                                             for s in open_hat['pattern']['steps']]
        closed_hat['pattern']['velocities'] = _vel_groove(closed_hat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.25, ghost_prob=0.05)

        layers = [kick, clap, open_hat, closed_hat, bass]

        # Chord stab — the harmonic centrepiece of most house tracks; often enters after the intro.
        stab = cls._maybe(_STABS, 0.8)
        if stab:
            stab = copy.deepcopy(stab)
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
            stab['entry_loop'] = random.choice([0, 2])
            layers.append(stab)

        pad = cls._maybe(_PADS, 0.4)
        if pad:
            layers.append(copy.deepcopy(pad))

        perc = cls._maybe(_PERCS, 0.5)
        if perc:
            perc = copy.deepcopy(perc)
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.15, ghost_prob=0.2)
            layers.append(perc)

        if random.random() < 0.5:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        cls._apply_key_coherence(layers)
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _auto, _chorus, _dist, _filt, _reverb, _midi_to_note,
    _note_to_midi, _vel_groove, _vel_snare, _on, _at,
)


def _vel_two_step(steps: list) -> list[float | None]:
    """The two kicks of the two-step (the one and the "and" of 3) hit hardest; doubles and pickups
    sit under them, so they push the groove without blurring which hits are the beat."""
    vels: list[float | None] = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 16 in (0, 10):
            vels.append(round(random.uniform(0.88, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.6, 0.78), 2))
    return vels


# MIDI D1. Every sub note is folded into the octave above it (37–69 Hz): low enough to be felt
# under the reese, high enough to still be heard on small speakers.
_SUB_FLOOR = 26


def _sub_under(bass: dict[str, Any]) -> dict[str, Any]:
    """A sine sub doubling the chosen bass line, note for note, folded into the sub register."""
    steps = [_N if s is None else _midi_to_note(_SUB_FLOOR + (_note_to_midi(s) - _SUB_FLOOR) % 12)
             for s in bass['pattern']['steps']]
    return _cfg('sub', 'sub', -9, bass['note_duration'], 'Synth',
                {'oscillator': {'type': 'sine'},
                 'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 1.0, 'release': 0.12}},
                [], steps, velocities=[_N if s is None else 0.85 for s in steps],
                sidechain='shallow')


# ---------------------------------------------------------------------------
# KICKS — the two-step: kick on the one and on the "and" of beat 3 (step 10)
# of every bar, against the snare on 2 and 4. Variations add a double, a
# lead-in or a pickup, but none puts a kick on every quarter — that would be
# a four-on-the-floor genre. Tight, punchy MembraneSynths: DnB kicks are short
# so the bass owns the low end between them.
# ---------------------------------------------------------------------------
_KICKS = [
    # K . . . S . . . . . K . S . . . | same — the plain two-step
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.6}},
         [], _on([0, 10, 16, 26], 'C1')),
    # Bar 2 doubles the "and" of 3 (0+10+11) — the push rollers use to turn the phrase
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.55}},
         [], _on([0, 10, 16, 26, 27], 'C1')),
    # Lead-in on the "a" of 2 (0+7+10) in bar 1, plain answer in bar 2
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.032, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.6}},
         [], _on([0, 7, 10, 16, 26], 'C1')),
    # Pickup kick on the last 16th, rolling back into the downbeat of the next loop
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0.01, 'release': 0.5}},
         [], _on([0, 10, 16, 26, 31], 'C1')),
    # Double on the one (0+2) in bar 1 — the "Think"-break shape inside the two-step
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.036, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.55}},
         [], _on([0, 2, 10, 16, 26], 'C1')),
    # 0+10+11 in both bars — the heavier, techstep version
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.27, 'sustain': 0.01, 'release': 0.5}},
         [_dist(0.12, 0.2)], _on([0, 10, 11, 16, 26, 27], 'C1')),
    # Bar 2 adds the "and" of 2 before the second kick — a skip that still lands on the two-step
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.034, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.31, 'sustain': 0.01, 'release': 0.6}},
         [], _on([0, 10, 16, 22, 26], 'C1')),
]

# ---------------------------------------------------------------------------
# SNARES — the backbeat on 2 and 4 (steps 4, 12, 20, 28) in every entry; it is
# the loudest, most exposed sound in DnB. Variation lives only in the ghost
# notes around it (_vel_snare keeps them at ghost level). A highpass keeps the
# noise crisp so the crack reads clean, not lo-fi.
# ---------------------------------------------------------------------------
_SNARES = [
    # . . . . S . . . . . . . S . . . | same — the clean backbeat
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 1100, 0.8), _reverb(0.9, 0.18)],
         _on([4, 12, 20, 28])),
    # Ghost on the last 16th of each bar, dragging into the downbeat
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 1300, 0.8), _reverb(0.8, 0.16)],
         _on([4, 12, 15, 20, 28, 31])),
    # Ghost on the "e" of 3 each bar — the rolling ghost between the two kicks
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.17, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 1000, 0.7), _reverb(1.0, 0.2)],
         _on([4, 9, 12, 20, 25, 28])),
    # Bar 2 answers with ghosts on the "a" of 2 and the "and" of 4
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 1400, 0.8), _reverb(0.7, 0.15)],
         _on([4, 12, 20, 23, 28, 30])),
    # Short ghost roll at the end of bar 2 turning the loop around
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 1200, 0.8), _reverb(0.9, 0.18)],
         _on([4, 12, 14, 20, 28, 29, 30, 31])),
    # Ghosts on the "and" of 2 — a lighter, liquid-style shuffle
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.09}},
         [_filt('highpass', 900, 0.7), _reverb(1.3, 0.24)],
         _on([4, 6, 12, 20, 22, 28])),
    # Ghost a 16th before beat 4 in both bars — a flam-like lean into the backbeat
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 1150, 0.8), _reverb(0.85, 0.17)],
         _on([4, 11, 12, 20, 27, 28])),
]

# ---------------------------------------------------------------------------
# SNARE BODIES — a short pitched thump under the backbeat only. Noise alone is
# all crack and no weight; the body is what makes the 2 and 4 hit like a real
# DnB snare. Ghosts get no body, so they stay ghosts.
# ---------------------------------------------------------------------------
_SNARE_BODIES = [
    _cfg('snare_body', 'snare', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.05}},
         [], _on([4, 12, 20, 28], 'G3')),
    _cfg('snare_body', 'snare', -10, '16n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 2.5, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [], _on([4, 12, 20, 28], 'A3')),
    _cfg('snare_body', 'snare', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [], _on([4, 12, 20, 28], 'E3')),
]

# ---------------------------------------------------------------------------
# HI-HATS — driving 8ths and 16ths (or a ride / shaker) that keep the 170+ BPM
# momentum between the sparse kicks. Velocity comes from _vel_groove.
# ---------------------------------------------------------------------------
_CLOSED_HAT = {'frequency': 420, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.02},
               'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 7000, 'octaves': 1.5}

_HIHATS = [
    # Straight 8ths — the plainest driving top
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth', _CLOSED_HAT, [],
         _on(list(range(0, 32, 2)), 'C4')),
    # Full 16ths — the rushing top of a roller
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.015},
          'harmonicity': 5.4, 'modulationIndex': 36, 'resonance': 7800, 'octaves': 1.6},
         [], _on(list(range(32)), 'C4')),
    # Offbeat 8ths, half-open — the classic DnB "tss" between the kick and snare
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 380, 'envelope': {'attack': 0.001, 'decay': 0.11, 'release': 0.06},
          'harmonicity': 5.1, 'modulationIndex': 30, 'resonance': 6000, 'octaves': 1.4},
         [], _on(list(range(2, 32, 4)), 'C4')),
    # 8ths with 16th pickups into each snare
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth', _CLOSED_HAT, [],
         _on([0, 2, 3, 6, 8, 10, 11, 14, 16, 18, 19, 22, 24, 26, 27, 30], 'C4')),
    # Ride on 8ths — the jazzier, liquid top
    _cfg('ride', 'hihat', -19, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.5, 'release': 0.3},
          'harmonicity': 5.1, 'modulationIndex': 28, 'resonance': 4200, 'octaves': 1.5},
         [], _on(list(range(0, 32, 2)), 'C4')),
    # Shaker 16ths — soft, airy drive
    _cfg('shaker', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.04, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 6500, 0.7)], _on(list(range(32)), 'C4')),
    # Rolling 16ths with breathing gaps on the backbeat
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 440, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.018},
          'harmonicity': 5.6, 'modulationIndex': 34, 'resonance': 7400, 'octaves': 1.5},
         [], _on([0, 1, 2, 3, 6, 7, 8, 10, 11, 14, 15, 16, 17, 18, 19, 22, 23, 24, 26, 27, 30, 31], 'C4')),
]

# ---------------------------------------------------------------------------
# TOPS — an optional second top loop (ride, shaker, tambourine) layered over
# the hats; stacking tops is how DnB fills the space above the breaks.
# ---------------------------------------------------------------------------
_TOPS = [
    _cfg('ride_top', 'perc', -23, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.45, 'release': 0.3},
          'harmonicity': 5.1, 'modulationIndex': 28, 'resonance': 4200, 'octaves': 1.5},
         [], _on(list(range(0, 32, 2)), 'C4')),
    _cfg('shaker_top', 'perc', -24, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.035, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 7000, 0.7)], _on(list(range(32)), 'C4')),
    _cfg('tambourine', 'perc', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [_filt('bandpass', 8500, 1.2)], _on(list(range(2, 32, 4)), 'C4')),
]

# ---------------------------------------------------------------------------
# BASSES — held reese and neuro lines, 8n to 2n. The reese is three detuned
# saws beating against each other (fatsawtooth), lowpassed and chorused, with a
# slow filter sweep across the loop so it breathes; the neuro entries are FM
# growls whose filter is swept harder. Notes mostly follow the two-step kick so
# bass and kick move together. Every line puts its root first and most often,
# which is the note key coherence locks to the track root.
# ---------------------------------------------------------------------------


def _reese(spread: int, cutoff: float) -> dict[str, Any]:
    return {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': spread},
            'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.85, 'release': 0.25},
            'filter': {'Q': 1.5, 'type': 'lowpass', 'rolloff': -24},
            'filterEnvelope': {'attack': 0.02, 'decay': 0.5, 'sustain': 0.6, 'release': 0.3,
                               'baseFrequency': cutoff, 'octaves': 2.5}}


_NEURO = {'harmonicity': 1.0, 'modulationIndex': 14,
          'oscillator': {'type': 'sawtooth'}, 'modulation': {'type': 'square'},
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.8, 'release': 0.15},
          'modulationEnvelope': {'attack': 0.02, 'decay': 0.25, 'sustain': 0.45, 'release': 0.2}}

_BASSES = [
    # A minor reese — root held across the two-step, falling to the b6 and b7 in bar 2
    _cfg('reese_bass', 'bass', -6, '2n', 'MonoSynth', _reese(30, 140),
         [_filt('lowpass', 700, 2), _chorus(0.5, 3.5, 0.6, 0.35), _dist(0.15, 0.2)],
         _at({0: 'A1', 10: 'A1', 16: 'A1', 26: 'F1', 29: 'G1'}),
         automation=[_auto('effect:0:frequency', 320, 1500, 'tri')]),
    # D minor techstep reese — wide detune, dark, sinking to the b6 and 5th
    _cfg('reese_bass', 'bass', -6, '2n', 'MonoSynth', _reese(42, 110),
         [_filt('lowpass', 600, 2.5), _chorus(0.35, 4, 0.7, 0.4), _dist(0.2, 0.25)],
         _at({0: 'D2', 10: 'D2', 16: 'Bb1', 24: 'A1', 28: 'C2'}),
         automation=[_auto('effect:0:frequency', 260, 1300, 'tri')]),
    # E minor neuro growl — dotted-8th stabs, the filter swept hard for the "talking" movement
    _cfg('neuro_bass', 'bass', -7, '8n', 'FMSynth', _NEURO,
         [_dist(0.45, 0.4), _filt('lowpass', 1200, 4)],
         _at({0: 'E2', 3: 'E2', 6: 'E2', 10: 'E2', 13: 'G2', 16: 'E2', 19: 'E2', 22: 'F2', 26: 'E2', 29: 'D2'}),
         automation=[_auto('effect:1:frequency', 400, 2600, 'tri')]),
    # G minor reese — octave lift on beat 3 of bar 1, then the minor third and 7th
    _cfg('reese_bass', 'bass', -6, '4n', 'MonoSynth', _reese(26, 150),
         [_filt('lowpass', 800, 2), _chorus(0.6, 3, 0.5, 0.3), _dist(0.12, 0.18)],
         _at({0: 'G1', 8: 'G2', 10: 'G1', 16: 'G1', 24: 'Bb1', 28: 'F1'}),
         automation=[_auto('effect:0:frequency', 350, 1700, 'ramp')]),
    # C minor neuro — busy syncopated growl with a ramped filter opening across the loop
    _cfg('neuro_bass', 'bass', -7, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 20,
          'oscillator': {'type': 'square'}, 'modulation': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.18, 'sustain': 0.75, 'release': 0.12},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.15, 'sustain': 0.5, 'release': 0.15}},
         [_dist(0.5, 0.4), _filt('lowpass', 1000, 5)],
         _at({0: 'C2', 2: 'C2', 6: 'Eb2', 10: 'C2', 16: 'C2', 22: 'C2', 26: 'Bb1', 30: 'G1'}),
         automation=[_auto('effect:1:frequency', 300, 2400, 'ramp')]),
    # F minor rolling square-reese — rounder, for the liquid end of the genre
    _cfg('reese_bass', 'bass', -6, '4n', 'MonoSynth',
         {'oscillator': {'type': 'fatsquare', 'count': 2, 'spread': 18},
          'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.8, 'release': 0.2},
          'filter': {'Q': 1.2, 'type': 'lowpass', 'rolloff': -24},
          'filterEnvelope': {'attack': 0.015, 'decay': 0.35, 'sustain': 0.5, 'release': 0.25,
                             'baseFrequency': 120, 'octaves': 2.2}},
         [_filt('lowpass', 650, 1.5), _chorus(0.8, 2.5, 0.5, 0.3)],
         _at({0: 'F1', 6: 'Ab1', 10: 'F1', 16: 'F1', 22: 'Eb2', 26: 'C2'}),
         automation=[_auto('effect:0:frequency', 380, 1200, 'tri')]),
    # B minor reese — two long notes per bar, the slow half-time movement of a breakdown roller
    _cfg('reese_bass', 'bass', -6, '2n', 'MonoSynth', _reese(36, 120),
         [_filt('lowpass', 650, 2.2), _chorus(0.3, 4, 0.7, 0.4), _dist(0.18, 0.22)],
         _at({0: 'B1', 10: 'B1', 16: 'G1', 26: 'A1'}),
         automation=[_auto('effect:0:frequency', 280, 1400, 'tri')]),
]

# ---------------------------------------------------------------------------
# ATMOSPHERES — long minor-7th/9th pads and drones behind the drums: the
# rolling-but-spacious feel of DnB. Chords put the tonic chord first so key
# coherence locks them to the bass root.
# ---------------------------------------------------------------------------
_ATMOSPHERES = [
    # Am9 -> Fmaj7, wide detuned saws behind a slowly opening lowpass
    _cfg('atmosphere', 'pad', -24, '1n', 'PolySynth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 24},
          'envelope': {'attack': 1.2, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5}},
         [_filt('lowpass', 1400, 0.7), _chorus(0.3, 4, 0.7, 0.5), _reverb(6.0, 0.75)],
         _at({0: 'A3,C4,E4,G4,B4', 16: 'F3,A3,C4,E4'}),
         automation=[_auto('effect:0:frequency', 800, 2200, 'tri')]),
    # Dm9 -> Bbmaj7, soft triangles for the liquid side
    _cfg('atmosphere', 'pad', -22, '1n', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.9, 'decay': 0.6, 'sustain': 0.75, 'release': 2.8}},
         [_chorus(0.4, 3.5, 0.6, 0.45), _reverb(5.5, 0.72)],
         _at({0: 'D3,F3,A3,C4,E4', 16: 'Bb2,D3,F3,A3'})),
    # D minor AM drone — slow harmonic movement every half-bar
    _cfg('atmosphere', 'pad', -21, '2n', 'AMSynth',
         {'harmonicity': 0.25, 'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.7, 'release': 2.0},
          'modulationEnvelope': {'attack': 0.6, 'decay': 0.3, 'sustain': 0.6, 'release': 2.0}},
         [_reverb(4.0, 0.75)],
         _at({0: 'D2', 8: 'A2', 16: 'D2', 24: 'G2'})),
    # Airy high triangle — shimmer above everything, very wet
    _cfg('airy_pad', 'pad', -26, '2n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.7, 'release': 3.0}},
         [_reverb(6.0, 0.9), _chorus(0.5, 4.0, 0.6, 0.5)],
         _at({0: 'A4', 8: 'E4', 16: 'A4', 24: 'G4'})),
]

# ---------------------------------------------------------------------------
# FILLS — snare rolls, reverse swells and tom runs on the last loop of an 8- or
# 16-bar phrase (DnB is arranged in 8/16-bar blocks).
# ---------------------------------------------------------------------------
_FILLS = [
    # 16th snare roll through the last two beats — every 8 bars
    _cfg('fill_roll', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 1200, 0.8), _reverb(0.5, 0.25)],
         _on(list(range(24, 32))),
         loop_modulo=4, loop_modulo_remainder=3),
    # Reverse cymbal sweep — every 16 bars
    _cfg('fill_sweep', 'perc', -16, '1n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 2.0, 'decay': 0.05, 'sustain': 0.95, 'release': 0.1}},
         [_reverb(1.5, 0.55), _filt('highpass', 1500, 1.2)],
         _on([0], 'C3'),
         loop_modulo=8, loop_modulo_remainder=7),
    # Descending tom run — every 16 bars
    _cfg('fill_tom', 'perc', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.3}},
         [_reverb(0.7, 0.3)],
         _at({22: 'G2', 24: 'F2', 26: 'E2', 28: 'D2', 30: 'C2'}),
         loop_modulo=8, loop_modulo_remainder=7),
]


class DrumAndBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.DRUM_AND_BASS
    BPM_RANGE = (170, 176)
    LEVEL_DB = -4.7
    PROFILE = GenreProfile(
        drums="Two-step: kick on 1 and the 'and' of 3, snare on 2 and 4, fast hi-hats",
        bass='Held reese or growling neuro bass over a sub',
        signature='A clean, punchy break with ghost snares; dark pads',
        mood='Fast, rolling, tense',
        key_trait='drums',
        kick_pattern='two_step',
        bass_pattern='reese',
    )
    SWING = 0.03  # A hair of shuffle humanizes the grid; DnB is played nearly straight
    KEY_ROLES = ('snare', 'bass')
    SIDECHAIN_DEPTH = 0.5
    SIDECHAIN_RELEASE = 0.4

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        body = copy.deepcopy(cls._pick(_SNARE_BODIES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_two_step(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        body['pattern']['velocities'] = _vel_snare(body['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        # Held reese notes want an even level; accents would read as random swells.
        bass['pattern']['velocities'] = [_N if s is None else round(random.uniform(0.78, 0.92), 2)
                                         for s in bass['pattern']['steps']]

        layers = [kick, snare, body, hihat, bass]

        top = cls._maybe(_TOPS, 0.4)
        if top:
            top = copy.deepcopy(top)
            top['pattern']['velocities'] = _vel_groove(top['pattern']['steps'])
            layers.append(top)

        atm = cls._maybe(_ATMOSPHERES, 0.5)
        if atm:
            atm = copy.deepcopy(atm)
            atm['entry_loop'] = random.choice([0, 2])
            layers.append(atm)

        if random.random() < 0.5:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        cls._apply_key_coherence(layers)
        # The sub is built from the bass after key coherence has moved it, so it is already in key and
        # folds straight into its register; transposing it as well could push it below 30 Hz.
        if random.random() < 0.5:
            layers.append(_sub_under(bass))
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _delay, _dist, _filt, _reverb, _vel, _vel_groove, _on, _at,
)


def _vel_break_kick(steps: list) -> list[float | None]:
    """Kicks on a beat hit full; the chopped in-between kicks sit a little under them, the way a
    sliced break keeps the drummer's own dynamics."""
    vels: list[float | None] = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 4 == 0:
            vels.append(round(random.uniform(0.86, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.62, 0.82), 2))
    return vels


def _vel_break_snare(steps: list) -> list[float | None]:
    """Backbeat full; the other break snares split between real ghosts and mid-level hits. An amen is
    not backbeat-plus-whispers — its off-beat snares are half the character."""
    vels: list[float | None] = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 32 in (4, 12, 20, 28):
            vels.append(round(random.uniform(0.82, 0.98), 2))
        elif random.random() < 0.55:
            vels.append(round(random.uniform(0.18, 0.34), 2))
        else:
            vels.append(round(random.uniform(0.4, 0.6), 2))
    return vels


def _vel_crescendo(steps: list) -> list[float | None]:
    """Rolls swell into the hit they lead to: each 32nd in a group of eight a little louder."""
    return [_N if s is None else round(0.18 + 0.34 * (i % 8) / 7, 2) for i, s in enumerate(steps)]


# ---------------------------------------------------------------------------
# BREAKS — the identity of jungle: a chopped amen-style break. Kick and snare
# are written together (_KICKS[i] pairs with _SNARES[i]) because a break edit
# is one gesture — mixing halves of different edits puts kicks and snares on
# top of each other. Every edit keeps the snare backbeat on 4, 12, 20, 28;
# around it the kick and snare are busy and syncopated, bar 2 is always a
# different edit from bar 1, and the kick never lands on every quarter.
# Short, gritty kicks; the snares are rawer than DnB (distortion, less
# filtering) because they stand in for a sampled, resampled break.
# ---------------------------------------------------------------------------
_KICKS = [
    # Amen bars 1-2: K . K . . . . . . . K K . . . . | K . K . . . . . . . K . . . . .
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.2, 0.25)], _on([0, 2, 10, 11, 16, 18, 26], 'C1')),
    # Amen bar-4 shape in bar 2 — the kick dodges the downbeat
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.032, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.28}},
         [_dist(0.18, 0.22)], _on([0, 2, 10, 18, 19, 26], 'C1')),
    # Amen bar 1, then a rushed bar 2 with the kick pulled to the "and" of 2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0.01, 'release': 0.32}},
         [_dist(0.22, 0.25)], _on([0, 2, 10, 11, 16, 22, 26], 'C1')),
    # Dotted-8th kick chop (0, 3, 6) — the syncopated, stumbling edit
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.036, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.21, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.2, 0.22)], _on([0, 3, 6, 10, 16, 19, 26, 27], 'C1')),
    # Think-style: lighter kick in bar 1, doubled pickups in bar 2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.26}},
         [_dist(0.15, 0.2)], _on([0, 6, 10, 16, 18, 22, 26], 'C1')),
    # Amen bar 1, then a stutter edit in bar 2 that leaves the kick to its last two hits
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.23, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.24, 0.26)], _on([0, 2, 10, 11, 16, 26, 27], 'C1')),
    # Half-bar reversal: bar 2 moves the second kick to beat 3 and pushes a pickup after it
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.034, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.2, 0.24)], _on([0, 2, 10, 16, 18, 24, 27], 'C1')),
]

_SNARES = [
    # . . . . S . . S . S . . S . . S | . . . . S . . S . S . . S . S .
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 700, 0.7), _dist(0.35, 0.35), _reverb(0.6, 0.14)],
         _on([4, 7, 9, 12, 15, 20, 23, 25, 28, 30])),
    # Amen bar 4: the extra snare on the "e" of 1 in bar 2
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.17, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 750, 0.7), _dist(0.3, 0.3), _reverb(0.5, 0.12)],
         _on([4, 7, 9, 12, 15, 17, 20, 23, 25, 28, 30])),
    # Bar 2 ends in a 16th snare run into the loop
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.09}},
         [_filt('highpass', 650, 0.7), _dist(0.4, 0.35), _reverb(0.7, 0.16)],
         _on([4, 7, 9, 12, 15, 20, 23, 25, 28, 29, 30, 31])),
    # Snares answering the dotted kick chop
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.1}},
         [_filt('highpass', 600, 0.7), _dist(0.3, 0.3), _reverb(0.6, 0.15)],
         _on([4, 9, 12, 14, 20, 23, 28, 31])),
    # Think-style ghosts on the "e" of 3 and the "and" of 4
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 800, 0.7), _dist(0.32, 0.3), _reverb(0.5, 0.12)],
         _on([4, 9, 12, 15, 20, 25, 28, 30])),
    # Stutter edit: the backbeat of bar 2 re-triggered on the next two 16ths
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.07}},
         [_filt('highpass', 700, 0.7), _dist(0.45, 0.4), _reverb(0.6, 0.14)],
         _on([4, 7, 9, 12, 15, 20, 21, 22, 25, 28, 31])),
    # Reversed half-bar: snares crowd the end of bar 2
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 720, 0.7), _dist(0.35, 0.32), _reverb(0.6, 0.14)],
         _on([4, 7, 9, 12, 14, 20, 22, 28, 30, 31])),
]

_BREAKS = list(zip(_KICKS, _SNARES))

# ---------------------------------------------------------------------------
# SNARE BODIES — a short, high-tuned membrane under every snare hit of the
# break (steps are replaced by the chosen snare's), so ghosts and backbeats
# alike have the ringing "crack" of a pitched-up break rather than bare noise.
# ---------------------------------------------------------------------------
_SNARE_BODIES = [
    _cfg('snare_body', 'snare', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.015, 'octaves': 1.8, 'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.05}},
         [_dist(0.25, 0.3)], _on([4, 12, 20, 28], 'A3')),
    _cfg('snare_body', 'snare', -10, '16n', 'MembraneSynth',
         {'pitchDecay': 0.012, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_dist(0.2, 0.25)], _on([4, 12, 20, 28], 'C4')),
    _cfg('snare_body', 'snare', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 1.6, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_dist(0.3, 0.3)], _on([4, 12, 20, 28], 'G3')),
]

# ---------------------------------------------------------------------------
# ROLLS & FLAMS — quiet 32nd-note snare decorations on top of the break
# (subdivision '32n': 64 steps, step 2n lines up with 16th step n). Flams land
# a 32nd before a backbeat; rolls swell into a hit or across the loop end.
# ---------------------------------------------------------------------------
_ROLL_SYNTH = {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03}}

_ROLLS = [
    # Flams before both backbeats of bar 2, then a 32nd roll across the loop end
    _cfg('snare_roll', 'snare', -10, '32n', 'NoiseSynth', _ROLL_SYNTH,
         [_filt('highpass', 900, 0.7), _dist(0.3, 0.3)],
         _on([39, 55, 56, 57, 58, 59, 60, 61, 62, 63], length=64), subdivision='32n'),
    # A flam into beat 2, then a roll building into beat 4 of bar 1
    _cfg('snare_roll', 'snare', -10, '32n', 'NoiseSynth', _ROLL_SYNTH,
         [_filt('highpass', 900, 0.7), _dist(0.3, 0.3)],
         _on([7, 17, 18, 19, 20, 21, 22, 23], length=64), subdivision='32n'),
    # Flams on all four backbeats — the doubled-up snare of a resampled break
    _cfg('snare_roll', 'snare', -11, '32n', 'NoiseSynth', _ROLL_SYNTH,
         [_filt('highpass', 1000, 0.7)],
         _on([7, 23, 39, 55], length=64), subdivision='32n'),
    # Buzz roll through the last beat of bar 2, crescendoing into the loop
    _cfg('snare_roll', 'snare', -11, '32n', 'NoiseSynth', _ROLL_SYNTH,
         [_filt('highpass', 850, 0.7), _dist(0.35, 0.3)],
         _on(list(range(48, 64)), length=64), subdivision='32n'),
]

# ---------------------------------------------------------------------------
# HI-HATS & RIDES — busy tops riding over the break. Ride 8ths are the amen's
# own cymbal; 16th hats and shakers make it rush.
# ---------------------------------------------------------------------------
_RIDE = {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.4, 'release': 0.25},
         'harmonicity': 5.1, 'modulationIndex': 30, 'resonance': 4500, 'octaves': 1.5}

_HIHATS = [
    # Ride 8ths — the amen's cymbal
    _cfg('ride', 'hihat', -17, '16n', 'MetalSynth', _RIDE, [],
         _on(list(range(0, 32, 2)), 'C4')),
    # Fast closed 16ths
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 480, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015},
          'harmonicity': 5.6, 'modulationIndex': 38, 'resonance': 8000, 'octaves': 1.6},
         [], _on(list(range(32)), 'C4')),
    # Shuffled 16ths with gaps — xx.x xx.x
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 450, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.02},
          'harmonicity': 5.2, 'modulationIndex': 34, 'resonance': 7500, 'octaves': 1.5},
         [], _on([i for i in range(32) if i % 4 != 2], 'C4')),
    # Ride 8ths with 16th pickups — the busier ride of a rolling edit
    _cfg('ride', 'hihat', -17, '16n', 'MetalSynth', _RIDE, [],
         _on([0, 2, 4, 6, 7, 8, 10, 12, 14, 15, 16, 18, 20, 22, 23, 24, 26, 27, 28, 30, 31], 'C4')),
    # Half-open hats in pairs on the "e" and "and" — the skippy feel of a sampled hat loop
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.09, 'release': 0.05},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 6500, 'octaves': 1.5},
         [], _on([1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 21, 22, 25, 26, 29, 30], 'C4')),
    # Shaker 16ths — the raw, sampled-percussion rush
    _cfg('shaker', 'hihat', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.045, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 6000, 0.7)], _on(list(range(32)), 'C4')),
]

# ---------------------------------------------------------------------------
# BASSES — dub / ragga sub bass: long sine or triangle notes (4n to 1n) moving
# slowly, half-time against the double-time break. The contrast between the
# rushing drums and the slow, deep bass is what jungle is. Some lines glide
# (portamento) between notes like a dub sound-system bass. Each line puts its
# root first and most often, which is the note key coherence locks to.
# ---------------------------------------------------------------------------
_BASSES = [
    # A minor — root, a drop to the 7th, the 5th underneath in bar 2
    _cfg('dub_bass', 'bass', -2, '2n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.9, 'release': 0.35}},
         [_dist(0.2, 0.2)],
         _at({0: 'A1', 12: 'G1', 16: 'A1', 24: 'E1', 28: 'G1'})),
    # D minor triangle — held root, answered by the minor third, falling to the 5th
    _cfg('dub_bass', 'bass', -3, '2n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.85, 'release': 0.4},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.4, 'sustain': 0.8, 'release': 0.4, 'baseFrequency': 220, 'octaves': 1}},
         [_filt('lowpass', 420, 1)],
         _at({0: 'D2', 10: 'D2', 14: 'F2', 16: 'D2', 24: 'A1', 28: 'C2'})),
    # B minor sine with glides — the sound-system bass bending between notes
    _cfg('dub_bass', 'bass', -2, '2n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'portamento': 0.06,
          'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.95, 'release': 0.3}},
         [_dist(0.15, 0.18)],
         _at({0: 'B1', 10: 'D2', 16: 'B1', 26: 'A1', 28: 'F#1'})),
    # A minor — one long note per bar, the slowest half-time movement
    _cfg('dub_bass', 'bass', -2, '1n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.9, 'release': 0.5}},
         [_dist(0.22, 0.22)],
         _at({0: 'A1', 16: 'F1', 28: 'G1'})),
    # C minor — the ragga octave jump on beat 3, then down through the 7th to the 5th
    _cfg('dub_bass', 'bass', -3, '4n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.85, 'release': 0.35},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.35, 'sustain': 0.75, 'release': 0.35, 'baseFrequency': 240, 'octaves': 1.2}},
         [_filt('lowpass', 500, 1)],
         _at({0: 'C2', 8: 'C3', 12: 'Bb1', 16: 'C2', 24: 'G1', 28: 'Bb1'})),
    # G minor — root pushed again on the "and" of 2, rising to the minor third
    _cfg('dub_bass', 'bass', -2, '4n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.9, 'release': 0.3}},
         [_dist(0.18, 0.2)],
         _at({0: 'G1', 6: 'G1', 10: 'Bb1', 16: 'G1', 22: 'F1', 26: 'D2'})),
    # A minor rising glide — slides up a minor third into bar 2 and a fourth beyond it
    _cfg('dub_bass', 'bass', -3, '2n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'portamento': 0.08,
          'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.9, 'release': 0.35},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.4, 'sustain': 0.8, 'release': 0.35, 'baseFrequency': 200, 'octaves': 1.2}},
         [_filt('lowpass', 450, 1)],
         _at({0: 'A1', 14: 'C2', 16: 'D2', 24: 'A1'})),
]

# ---------------------------------------------------------------------------
# SKANKS — the ragga offbeat chord: a short organ-ish minor triad on the "and"
# of every beat, thrown into a dub delay. Root chord first and most often.
# ---------------------------------------------------------------------------
_SKANK_SYNTH = {'oscillator': {'type': 'square'},
                'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.0, 'release': 0.06}}

_STABS = [
    # Am on every offbeat 8th, G at the end of bar 2
    _cfg('skank', 'stab', -18, '16n', 'PolySynth', _SKANK_SYNTH,
         [_filt('highpass', 450, 0.7), _delay('8n.', 0.35, 0.25), _reverb(1.2, 0.18)],
         _at({2: 'A3,C4,E4', 6: 'A3,C4,E4', 10: 'A3,C4,E4', 14: 'A3,C4,E4',
              18: 'A3,C4,E4', 22: 'A3,C4,E4', 26: 'G3,B3,D4', 30: 'G3,B3,D4'})),
    # Dm, dropping to C for the second half of bar 2
    _cfg('skank', 'stab', -19, '16n', 'PolySynth',
         {'oscillator': {'type': 'custom', 'partials': [1, 0.6, 0.4, 0.25, 0.15]},
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.0, 'release': 0.08}},
         [_filt('highpass', 400, 0.7), _delay('4n', 0.4, 0.28), _reverb(1.4, 0.2)],
         _at({2: 'D4,F4,A4', 6: 'D4,F4,A4', 10: 'D4,F4,A4', 14: 'D4,F4,A4',
              18: 'D4,F4,A4', 22: 'D4,F4,A4', 26: 'C4,E4,G4', 30: 'C4,E4,G4'})),
    # Double skank — the offbeat plus the 16th after it, Gm moving to F
    _cfg('skank', 'stab', -19, '16n', 'PolySynth', _SKANK_SYNTH,
         [_filt('highpass', 500, 0.7), _delay('8n.', 0.3, 0.22), _reverb(1.0, 0.16)],
         _at({2: 'G3,Bb3,D4', 6: 'G3,Bb3,D4', 7: 'G3,Bb3,D4', 10: 'G3,Bb3,D4', 14: 'G3,Bb3,D4', 15: 'G3,Bb3,D4',
              18: 'G3,Bb3,D4', 22: 'G3,Bb3,D4', 23: 'G3,Bb3,D4', 26: 'F3,A3,C4', 30: 'F3,A3,C4', 31: 'F3,A3,C4'})),
    # Sparse Em skank on the "and" of 2 and 4 only, drowned in a long dub echo
    _cfg('skank', 'stab', -17, '16n', 'PolySynth', _SKANK_SYNTH,
         [_filt('highpass', 450, 0.7), _delay('8n.', 0.55, 0.38), _reverb(2.0, 0.25)],
         _at({6: 'E4,G4,B4', 14: 'E4,G4,B4', 22: 'E4,G4,B4', 30: 'E4,G4,B4'})),
]

# ---------------------------------------------------------------------------
# DUB FX — a gliding dub siren (portamento between the notes makes the wail)
# heard every other loop, or a dark pad under the break.
# ---------------------------------------------------------------------------
_SIRENS = [
    # Fast up-down wail between root and octave
    _cfg('dub_siren', 'lead', -22, '8n', 'Synth',
         {'oscillator': {'type': 'square'}, 'portamento': 0.12,
          'envelope': {'attack': 0.02, 'decay': 0.1, 'sustain': 0.9, 'release': 0.3}},
         [_filt('lowpass', 2200, 1), _delay('8n.', 0.5, 0.4), _reverb(2.5, 0.35)],
         _at({0: 'A4', 4: 'A5', 6: 'A4', 8: 'A5', 10: 'A4', 12: 'A5'}),
         loop_modulo=2, loop_modulo_remainder=1),
    # Slow rising siren between root and fifth
    _cfg('dub_siren', 'lead', -22, '4n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'portamento': 0.3,
          'envelope': {'attack': 0.05, 'decay': 0.1, 'sustain': 0.9, 'release': 0.5}},
         [_delay('4n', 0.55, 0.4), _reverb(3.0, 0.4)],
         _at({0: 'E5', 8: 'B5', 16: 'E5', 24: 'B5'}),
         loop_modulo=2, loop_modulo_remainder=1),
]

_PADS = [
    _cfg('pad', 'pad', -20, '2n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.7, 'release': 1.5}},
         [_reverb(4.5, 0.8), _filt('lowpass', 2000, 2)],
         _at({0: 'A3', 8: 'C4', 16: 'A3', 24: 'G3'})),
    _cfg('pad', 'pad', -21, '2n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.4, 'decay': 0.3, 'sustain': 0.75, 'release': 1.8},
          'modulationEnvelope': {'attack': 0.6, 'decay': 0.2, 'sustain': 0.8, 'release': 1.5}},
         [_reverb(5.0, 0.82)],
         _at({0: 'E3', 8: 'G3', 16: 'E3', 24: 'D3'})),
    _cfg('pad', 'pad', -21, '1n', 'PolySynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.72, 'release': 2.0}},
         [_reverb(5.5, 0.85)],
         _at({0: 'D3,F3,A3', 16: 'Bb2,D3,F3'})),
]


class JungleTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.JUNGLE
    BPM_RANGE = (160, 170)
    LEVEL_DB = -8.4
    SWING = 0.05  # Light shuffle — the break's own feel, rawer than DnB's near-straight grid
    KEY_ROLES = ('snare', 'bass')
    SIDECHAIN_DEPTH = 0.4
    SIDECHAIN_RELEASE = 0.4

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick, snare = copy.deepcopy(cls._pick(_BREAKS))
        body = copy.deepcopy(cls._pick(_SNARE_BODIES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_break_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_break_snare(snare['pattern']['steps'])
        # The body follows every hit of this break's snare, at the same dynamics.
        body_note = next(s for s in body['pattern']['steps'] if s is not None)
        body['pattern']['steps'] = [body_note if s is not None else _N for s in snare['pattern']['steps']]
        body['pattern']['velocities'] = list(snare['pattern']['velocities'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        # Long dub notes want an even level; accents would read as random swells.
        bass['pattern']['velocities'] = [_N if s is None else round(random.uniform(0.82, 0.95), 2)
                                         for s in bass['pattern']['steps']]

        layers = [kick, snare, body, hihat, bass]

        roll = cls._maybe(_ROLLS, 0.6)
        if roll:
            roll = copy.deepcopy(roll)
            roll['pattern']['velocities'] = _vel_crescendo(roll['pattern']['steps'])
            layers.append(roll)

        # Jungle stacks tops more than DnB does; a second, quieter top makes it rush.
        if random.random() < 0.45:
            other = [h for h in _HIHATS if h['id'] != hihat['id']]
            top = copy.deepcopy(random.choice(other))
            top['pattern']['velocities'] = _vel_groove(top['pattern']['steps'])
            top['id'] = f'{top["id"]}_top'
            top['volume'] = top['volume'] - 5
            layers.append(top)

        stab = cls._maybe(_STABS, 0.45)
        if stab:
            stab = copy.deepcopy(stab)
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
            stab['entry_loop'] = random.choice([0, 2])
            layers.append(stab)

        # A siren or a pad, never both: either one alone already fills the space above the bass.
        dub_fx = random.random()
        if dub_fx < 0.35:
            layers.append(copy.deepcopy(cls._pick(_SIRENS)))
        elif dub_fx < 0.7:
            pad = copy.deepcopy(cls._pick(_PADS))
            pad['entry_loop'] = random.choice([0, 2])
            layers.append(pad)

        cls._apply_key_coherence(layers)
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _pingpong, _auto, _vel,
    _vel_snare, _on, _vel_flat,
)

_STEPS = 32


def _gallop(root: str, changes: dict[int, str | None] | None = None) -> list[str | None]:
    """K . B B, the progressive gallop: two bass 16ths on the back half of every beat. The 16th
    straight after the kick stays empty — that gap is what separates it from full-on's K-B-B-B.
    `changes` swaps single steps for octave jumps, passing notes and dropped notes."""
    steps = _on((i for i in range(_STEPS) if i % 4 in (2, 3)), root)
    for i, note in (changes or {}).items():
        steps[i] = note
    return steps


def _offbeat(root: str, changes: dict[int, str | None] | None = None) -> list[str | None]:
    """K . B ., the older offbeat bass: one note on the "and" of every beat."""
    steps = _on(range(2, _STEPS, 4), root)
    for i, note in (changes or {}).items():
        steps[i] = note
    return steps


# The second note of the gallop is a little softer than the first: "da-dum" rather than two equal
# hits, which gives the lilt prog grooves on.
_GALLOP_LEVELS = {2: (0.86, 0.94), 3: (0.72, 0.82)}


def _vel_gallop(steps: list) -> list[float | None]:
    return [None if s is None else round(random.uniform(*_GALLOP_LEVELS.get(i % 4, (0.8, 0.88))), 2)
            for i, s in enumerate(steps)]


# The swung feel of prog percussion without moving anything off the grid: the "a" of each beat is
# the loudest, the "e" next, the beat and the "and" quietest — the 16ths lean forward into the beat.
_SHUFFLE_LEVELS = {0: (0.3, 0.4), 1: (0.55, 0.68), 2: (0.38, 0.48), 3: (0.75, 0.9)}


def _vel_shuffle(steps: list) -> list[float | None]:
    return [None if s is None else round(random.uniform(*_SHUFFLE_LEVELS[i % 4]), 2)
            for i, s in enumerate(steps)]


# ---------------------------------------------------------------------------
# KICKS — strict four-on-the-floor, deeper and a touch longer than full-on:
# slower pitch drop, lower tuning, more body. The gallop starts on the "and",
# so the kick has an 8th of space to ring out.
# ---------------------------------------------------------------------------
_KICKS = [
    # Deep punch — the reference prog kick
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0, 'release': 0.08}},
         [], _on(range(0, _STEPS, 4), 'F1')),
    # Round and warm — lowpassed, low tuning
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0, 'release': 0.08}},
         [_filt('lowpass', 1800, 0.7)], _on(range(0, _STEPS, 4), 'E1')),
    # Punchy — tighter sweep for the faster end of the range
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0, 'release': 0.07}},
         [], _on(range(0, _STEPS, 4), 'G1')),
    # Soft-clipped — a little drive for weight
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 6.5,
          'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0, 'release': 0.08}},
         [_dist(0.12, 0.2)], _on(range(0, _STEPS, 4), 'F#1')),
    # Dub room — a hint of space around the thump
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.9, 0.08)], _on(range(0, _STEPS, 4), 'F1')),
    # Triangle thump — rounder top end that still reads on small speakers
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 6, 'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0, 'release': 0.07}},
         [_filt('lowpass', 2000, 0.7)], _on(range(0, _STEPS, 4), 'G1')),
]

# ---------------------------------------------------------------------------
# BASSES — the gallop "K . B B" is the main shape; a few entries use the older
# single offbeat "K . B .". Never a note on the 16th right after the kick.
# Rounder and deeper than full-on: low-index FM or a saw/square behind a low
# cutoff with little resonance, almost no drive, slightly longer decay
# (~0.15), and only a gentle filter drift over the loop. Written on A1.
# ---------------------------------------------------------------------------
# Low-index FM: a sine body with a soft knock on the attack — round, not buzzy.
_FM_ROUND = {
    'harmonicity': 1, 'modulationIndex': 3.5,
    'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0, 'release': 0.05},
    'modulationEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05},
}
_SAW_DEEP = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 1.2, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0, 'release': 0.05},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.05,
                       'baseFrequency': 110, 'octaves': 2.6},
}
# Square behind a low cutoff: hollow and woody.
_SQUARE_HOLLOW = {
    'oscillator': {'type': 'square'},
    'filter': {'Q': 1, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.16, 'sustain': 0, 'release': 0.06},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0, 'release': 0.05,
                       'baseFrequency': 100, 'octaves': 2.2},
}
# The offbeat bass holds a longer note per beat, a little more open.
_SAW_OFFBEAT = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 1.5, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.003, 'decay': 0.22, 'sustain': 0, 'release': 0.08},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.16, 'sustain': 0, 'release': 0.08,
                       'baseFrequency': 140, 'octaves': 2.8},
}

_BASSES = [
    # Pure gallop — one note, round FM
    _cfg('bass', 'bass', -6, '16n', 'FMSynth', _FM_ROUND,
         [_filt('lowpass', 650, 1.5)],
         _gallop('A1'),
         automation=[_auto('effect:0:frequency', 450, 800, 'tri')]),
    # Octave lift into each bar
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SAW_DEEP,
         [_filt('lowpass', 600, 1.5)],
         _gallop('A1', {15: 'A2', 31: 'A2'}),
         automation=[_auto('effect:0:frequency', 420, 760, 'tri')]),
    # Flat seven closing bar 2
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _SQUARE_HOLLOW,
         [_filt('lowpass', 560, 1.2)],
         _gallop('A1', {30: 'G1', 31: 'G1'}),
         automation=[_auto('effect:0:frequency', 400, 700, 'tri')]),
    # Minor-third answer in bar 2
    _cfg('bass', 'bass', -6, '16n', 'FMSynth', _FM_ROUND,
         [_dist(0.08, 0.12), _filt('lowpass', 620, 1.5)],
         _gallop('A1', {22: 'C2', 23: 'C2', 30: 'D2', 31: 'C2'}),
         automation=[_auto('effect:1:frequency', 450, 820, 'tri')]),
    # Old-school offbeat — one longer note on every "and"
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth', _SAW_OFFBEAT,
         [_filt('lowpass', 700, 1.5)],
         _offbeat('A1'),
         automation=[_auto('effect:0:frequency', 500, 900, 'tri')]),
    # Offbeat with an octave answer and a flat-seven turn
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth', _SAW_OFFBEAT,
         [_filt('lowpass', 680, 1.5)],
         _offbeat('A1', {14: 'A2', 30: 'G1'}),
         automation=[_auto('effect:0:frequency', 480, 860, 'tri')]),
    # Gallop with a breath — a low fifth, then the last 16th left empty
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _SAW_DEEP,
         [_filt('lowpass', 620, 1.5)],
         _gallop('A1', {27: 'E1', 31: _N}),
         automation=[_auto('effect:0:frequency', 420, 780, 'tri')]),
]

# ---------------------------------------------------------------------------
# OPEN HATS — every offbeat, softer and airier than full-on.
# ---------------------------------------------------------------------------
_OFFBEATS = range(2, _STEPS, 4)

_OPEN_HATS = [
    # Soft white — the default
    _cfg('open_hat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 7000, 0.8)], _on(_OFFBEATS, 'C4')),
    # Darker pink — rounder hat for the deeper tracks
    _cfg('open_hat', 'hihat', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0, 'release': 0.05}},
         [_filt('bandpass', 7500, 1)], _on(_OFFBEATS, 'C4')),
    # Long airy — longer tail with a little room
    _cfg('open_hat', 'hihat', -17, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.003, 'decay': 0.2, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 8500, 0.8), _reverb(1.0, 0.15)], _on(_OFFBEATS, 'C4')),
    # Tight chick
    _cfg('open_hat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 7200, 1)], _on(_OFFBEATS, 'C4')),
    # FM metal — inharmonic cluster above a highpass
    _cfg('open_hat', 'hihat', -19, '16n', 'FMSynth',
         {'harmonicity': 5.1, 'modulationIndex': 36,
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 6500, 1)], _on(_OFFBEATS, 'A5')),
]

# ---------------------------------------------------------------------------
# PERCS — the groove layer: 16th shakers and syncopated rims / toms, accented
# by _vel_shuffle so they swing without leaving the grid.
# ---------------------------------------------------------------------------
_PERCS = [
    # Shaker 16ths — soft attack makes it a swish, not a tick
    _cfg('shaker', 'perc', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.008, 'decay': 0.045, 'sustain': 0, 'release': 0.02}},
         [_filt('bandpass', 6000, 1.2)], _on(range(_STEPS), 'C4'), pan=-0.25),
    # Shaker that leaves the kick alone
    _cfg('shaker', 'perc', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.006, 'decay': 0.05, 'sustain': 0, 'release': 0.02}},
         [_filt('bandpass', 5000, 1.2)], _on((i for i in range(_STEPS) if i % 4 != 0), 'C4'), pan=-0.25),
    # Woody rim in a 3-3-2 figure, thrown into a dub delay
    _cfg('rim', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.004, 'octaves': 1.6,
          'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.02}},
         [_delay('8n.', 0.3, 0.2)], _on([3, 6, 11, 14, 19, 22, 27, 30], 'E5'), pan=0.3),
    # Tom pair answering the kick
    _cfg('toms', 'perc', -15, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 2.5,
          'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.05}},
         [_reverb(1.0, 0.15)],
         [_N,_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,_N,'A2',_N,
          _N,_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,'A2','A2',_N], pan=-0.15),
    # Ticky ride on the off-16ths — the quietest, most swung layer
    _cfg('ride_tick', 'perc', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 10000, 1)], _on(range(1, _STEPS, 2), 'C4'), pan=0.3),
    # Conga-ish hand drum, syncopated around the gallop
    _cfg('conga', 'perc', -17, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 2,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.04}},
         [_reverb(0.8, 0.12)],
         [_N,_N,_N,'G3',_N,_N,_N,'C4',_N,_N,'G3',_N,_N,_N,_N,'C4',
          _N,_N,_N,'G3',_N,_N,_N,'C4',_N,_N,'G3',_N,_N,_N,'G3','C4'], pan=-0.3),
]

# ---------------------------------------------------------------------------
# CLAPS — a light clap or rim on beats 2 and 4. Optional; prog uses it, full-on
# mostly doesn't.
# ---------------------------------------------------------------------------
_BACKBEAT = [4, 12, 20, 28]

_CLAPS = [
    # Clap — pink noise around 1.5 kHz with a short room
    _cfg('clap', 'snare', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_filt('bandpass', 1500, 0.9), _reverb(1.0, 0.22)], _on(_BACKBEAT, 'C4')),
    # Rim click
    _cfg('rim_click', 'snare', -16, '16n', 'MembraneSynth',
         {'pitchDecay': 0.003, 'octaves': 1.5,
          'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.02}},
         [_reverb(0.7, 0.15)], _on(_BACKBEAT, 'F#5')),
    # Snappy clap — brighter, shorter
    _cfg('clap', 'snare', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.04}},
         [_filt('bandpass', 2000, 1.4), _reverb(0.8, 0.18)], _on(_BACKBEAT, 'C4')),
    # Dub clap — echoing off into the next beat
    _cfg('clap', 'snare', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [_filt('bandpass', 1300, 0.9), _delay('8n.', 0.35, 0.18), _reverb(1.4, 0.2)], _on(_BACKBEAT, 'C4')),
]

# ---------------------------------------------------------------------------
# PLUCKS — the sparse, delay-heavy melodic element: two to six notes in two
# bars, left to repeat in ping-pong echoes. Minimal and hypnotic by design.
# ---------------------------------------------------------------------------
_TRI_PLUCK = {
    'oscillator': {'type': 'triangle'},
    'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0, 'release': 0.2},
}
_FM_PLUCK = {
    'harmonicity': 2, 'modulationIndex': 6,
    'envelope': {'attack': 0.002, 'decay': 0.22, 'sustain': 0, 'release': 0.2},
    'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.1},
}
_SAW_PLUCK = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'Q': 4, 'type': 'lowpass', 'rolloff': -24},
    'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0, 'release': 0.15},
    'filterEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.1,
                       'baseFrequency': 400, 'octaves': 3},
}

_PLUCKS = [
    # Two-note dub motif
    _cfg('pluck', 'lead', -14, '16n', 'Synth', _TRI_PLUCK,
         [_pingpong('8n.', 0.45, 0.32), _reverb(2.5, 0.3)],
         [_N,_N,_N,_N,_N,_N,'A4',_N,_N,_N,_N,_N,_N,_N,'E5',_N,
          _N,_N,_N,_N,_N,_N,'A4',_N,_N,_N,'C5',_N,_N,_N,_N,_N]),
    # Rising three, twice
    _cfg('pluck', 'lead', -15, '16n', 'FMSynth', _FM_PLUCK,
         [_pingpong('8n.', 0.42, 0.3), _reverb(2.8, 0.3)],
         [_N,_N,'A4',_N,_N,'C5',_N,_N,_N,_N,'E5',_N,_N,_N,_N,_N,
          _N,_N,'A4',_N,_N,'C5',_N,_N,_N,_N,'D5',_N,_N,_N,'A4',_N]),
    # Offset hits that let the dotted-8th echo fill the gaps
    _cfg('pluck', 'lead', -14, '16n', 'Synth', _TRI_PLUCK,
         [_pingpong('8n.', 0.5, 0.35), _reverb(2.5, 0.3)],
         [_N,_N,'A4',_N,_N,_N,_N,_N,_N,_N,_N,'E5',_N,_N,_N,_N,
          _N,_N,'A4',_N,_N,_N,_N,_N,_N,_N,_N,'G5',_N,_N,_N,_N]),
    # Low resonant pluck, filter drifting open
    _cfg('pluck', 'lead', -16, '16n', 'MonoSynth', _SAW_PLUCK,
         [_filt('lowpass', 1400, 2), _pingpong('8n.', 0.4, 0.28), _reverb(2.0, 0.25)],
         [_N,_N,_N,'A3',_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'C4',_N,
          _N,_N,_N,'A3',_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N],
         automation=[_auto('effect:0:frequency', 900, 2600, 'tri')]),
    # Bell answer — bar 2 only
    _cfg('pluck', 'lead', -16, '16n', 'FMSynth', _FM_PLUCK,
         [_pingpong('8n.', 0.45, 0.32), _reverb(3.0, 0.35)],
         [_N]*16 + [_N,_N,'A5',_N,_N,_N,'E5',_N,_N,_N,'A5',_N,_N,'C6',_N,_N]),
    # Hypnotic repeat — the same note on the offbeats of bar 1, a phrygian rub at the end
    _cfg('pluck', 'lead', -15, '16n', 'Synth', _TRI_PLUCK,
         [_pingpong('8n.', 0.4, 0.3), _reverb(2.2, 0.28)],
         [_N,_N,'A4',_N,_N,_N,'A4',_N,_N,_N,'A4',_N,_N,_N,'Bb4',_N] + [_N]*16),
]

# ---------------------------------------------------------------------------
# STABS — dub chord stabs: one short chord, a few times in two bars, fed into
# long feedback delay so the echoes carry the harmony.
# ---------------------------------------------------------------------------
_STAB_VOICE = {
    'oscillator': {'type': 'sawtooth'},
    'envelope': {'attack': 0.003, 'decay': 0.16, 'sustain': 0, 'release': 0.12},
}

_STABS = [
    # Minor seventh on the "and" of beat 2, both bars
    _cfg('dub_stab', 'stab', -17, '16n', 'PolySynth', _STAB_VOICE,
         [_filt('lowpass', 1800, 1), _delay('8n.', 0.5, 0.35), _reverb(3.0, 0.35)],
         _on([6, 22], 'A3,C4,E4,G4'),
         automation=[_auto('effect:0:frequency', 1000, 2800, 'tri')]),
    # Minor triad on the "a" of beat 1
    _cfg('dub_stab', 'stab', -17, '16n', 'PolySynth', _STAB_VOICE,
         [_filt('lowpass', 1600, 1), _delay('8n.', 0.55, 0.35), _reverb(3.0, 0.35)],
         _on([3, 19], 'A3,C4,E4'),
         automation=[_auto('effect:0:frequency', 900, 2500, 'tri')]),
    # Suspended fourth resolving to minor
    _cfg('dub_stab', 'stab', -18, '16n', 'PolySynth', _STAB_VOICE,
         [_filt('lowpass', 2000, 1), _delay('8n.', 0.5, 0.32), _reverb(3.2, 0.35)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3,D4,E4',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3,D4,E4',_N,_N,_N,'A3,C4,E4',_N]),
    # Minor ninth, darker voicing
    _cfg('dub_stab', 'stab', -18, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0, 'release': 0.12}},
         [_filt('lowpass', 1400, 1.5), _delay('8n.', 0.5, 0.35), _reverb(3.5, 0.4)],
         _on([6, 14], 'A3,C4,G4,B4'),
         automation=[_auto('effect:0:frequency', 800, 2200, 'tri')]),
    # Phrygian pair — minor, then the flat-two chord
    _cfg('dub_stab', 'stab', -17, '16n', 'PolySynth', _STAB_VOICE,
         [_filt('lowpass', 1700, 1), _delay('8n.', 0.5, 0.35), _reverb(3.0, 0.35)],
         ['A3,C4,E4' if i == 2 else 'Bb3,D4,F4' if i == 18 else _N for i in range(_STEPS)]),
]

# ---------------------------------------------------------------------------
# ATMOSPHERES — slow, wide pads and washes; pumping hard on the sidechain.
# ---------------------------------------------------------------------------
_ATMOS = [
    # Wide minor-ninth pad, filter breathing
    _cfg('atmos', 'pad', -22, '1m', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5}},
         [_chorus(0.4, 3.5, 0.6, 0.4), _filt('lowpass', 1600, 0.8), _reverb(6.0, 0.6)],
         ['A3,E4,B4'] + [_N]*15 + ['G3,D4,A4'] + [_N]*15,
         automation=[_auto('effect:1:frequency', 900, 2400, 'tri')],
         entry_loop=2),
    # AM drone on the root
    _cfg('atmos', 'pad', -21, '1m', 'AMSynth',
         {'harmonicity': 1.5,
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.85, 'release': 2.5},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}},
         [_filt('lowpass', 1200, 1), _reverb(5.0, 0.55)],
         _on([0, 16], 'A3')),
    # Breathing noise wash — a bandpass sweeping through pink noise
    _cfg('atmos', 'pad', -24, '1m', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.9, 'release': 2.0}},
         [_filt('bandpass', 1200, 2), _reverb(5.0, 0.6)],
         _on([0, 16], 'A3'),
         automation=[_auto('effect:0:frequency', 400, 2600, 'tri')]),
    # FM shimmer — glassy root, a fifth at the end of the phrase
    _cfg('atmos', 'pad', -23, '2n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 1.2,
          'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.7, 'release': 2.0},
          'modulationEnvelope': {'attack': 0.8, 'decay': 0.4, 'sustain': 0.6, 'release': 2.0}},
         [_chorus(0.3, 3, 0.5, 0.35), _reverb(6.0, 0.65)],
         ['A4' if i in (0, 16) else 'E5' if i == 24 else _N for i in range(_STEPS)],
         entry_loop=2),
]


class ProgressivePsyTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PROGRESSIVE_PSY
    BPM_RANGE = (134, 140)
    LEVEL_DB = 0.0
    PROFILE = GenreProfile(
        drums='Deep, round four-on-the-floor kick; offbeat hat, swung shakers, light clap on 2 and 4',
        bass='Galloping: two notes on the last two 16ths of each beat (K . B B), never right after the kick',
        signature='Sparse: one delay-heavy pluck or dub stab, lots of space',
        mood='Deep, groovy, hypnotic',
        key_trait='bass',
        kick_pattern='four',
        bass_pattern='gallop',
    )
    KEY_ROLES = ('bass',)
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.25

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))

        kick['pattern']['velocities'] = _vel_flat(kick['pattern']['steps'], 0.92, 1.0)
        bass['pattern']['velocities'] = _vel_gallop(bass['pattern']['steps'])
        open_hat['pattern']['velocities'] = _vel_flat(open_hat['pattern']['steps'], 0.62, 0.8)

        layers = [kick, bass, open_hat]

        if random.random() < 0.85:
            perc = copy.deepcopy(cls._pick(_PERCS))
            perc['pattern']['velocities'] = _vel_shuffle(perc['pattern']['steps'])
            layers.append(perc)

        if random.random() < 0.6:
            clap = copy.deepcopy(cls._pick(_CLAPS))
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        # One melodic element at most — prog is minimal; the space is part of the sound.
        roll = random.random()
        melodic = None
        if roll < 0.5:
            melodic = copy.deepcopy(cls._pick(_PLUCKS))
        elif roll < 0.85:
            melodic = copy.deepcopy(cls._pick(_STABS))
        if melodic is not None:
            melodic['pattern']['velocities'] = _vel(melodic['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
            if random.random() < 0.35:
                melodic['entry_loop'] = 2
            layers.append(melodic)

        if random.random() < 0.5:
            layers.append(copy.deepcopy(cls._pick(_ATMOS)))

        cls._apply_key_coherence(layers)
        return layers

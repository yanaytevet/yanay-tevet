import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus, _filt, _delay, _auto, _slides, _vel,
    _vel_groove, _vel_kick, _vel_snare, _clear_kick_steps, _tune_kick, _vel_rumble,
)

# D1 (37 Hz) up to C#2 (69 Hz): low enough that the distorted tail growls rather than honks.
_KICK_LOWEST_MIDI = 26

# ---------------------------------------------------------------------------
# KICKS — the centrepiece: loud, saturated to the point of square-ish, with a
# long tail so the distortion turns it into a pitched "doooff". Every entry
# drives hard; some chain two distortion stages with a filter between them, as
# hard techno producers do. A few add a 16th lead-in before a downbeat. The note
# is a placeholder; _tune_kick retunes it to the track root.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.8, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Dark rumbling tail — fizz rolled off after the drive
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 0.75}},
         [_dist(0.9, 0.85), _filt('lowpass', 3500, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Punchier, shorter sweep, a little room
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.75, 0.75), _reverb(0.6, 0.1)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Longest, most saturated tail — schranz territory
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.02, 'release': 0.8}},
         [_dist(0.95, 0.9), _filt('highpass', 35, 0.7)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Double distortion: drive, tame the top, drive again
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.6, 0.7), _filt('lowpass', 2500, 1.5), _dist(0.7, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Extra 16th into the loop restart
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.85, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Extra 16th into both bar downbeats
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 7.5, 'envelope': {'attack': 0.001, 'decay': 0.46, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.8, 0.8), _filt('lowpass', 4000, 0.7)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
]

# ---------------------------------------------------------------------------
# RUMBLES — the rolling hard techno low end: three 16ths after every kick,
# driven much harder than techno's rumble and lowpassed higher, so it growls
# "da-da-da" instead of just humming. The deep sidechain at full depth makes
# it pump against the kick.
# ---------------------------------------------------------------------------
_RUMBLES = [
    # Kick-tail rumble — membrane thump into a room, then crushed
    _cfg('rumble', 'bass', -1, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.08}},
         [_reverb(2.0, 0.6), _dist(0.85, 0.85), _filt('lowpass', 260, 1.2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1'],
         sidechain='deep'),
    # Rolling saw — articulated 16ths, short room, steps up at the end of the loop
    _cfg('rumble', 'bass', -3, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.1, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.15, 'release': 0.06,
                             'baseFrequency': 80, 'octaves': 2.5}},
         [_dist(0.9, 0.85), _reverb(1.5, 0.4), _filt('lowpass', 300, 1.5)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'C2','C2','C2'],
         sidechain='deep'),
    # Square rumble with a lowpass that opens across the loop — the growl gets brighter
    _cfg('rumble', 'bass', -2, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.15, 'release': 0.08},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.2, 'release': 0.08,
                             'baseFrequency': 70, 'octaves': 2.5}},
         [_dist(0.8, 0.8), _reverb(2.5, 0.5), _filt('lowpass', 220, 2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'G1','G1','G1'],
         automation=[_auto('effect:2:frequency', 160, 420, 'tri')],
         sidechain='deep'),
    # Phrygian rumble — the half-step lift is the dark "industrial" colour
    _cfg('rumble', 'bass', -2, '16n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.2, 'release': 0.1},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.3, 'release': 0.08,
                             'baseFrequency': 60, 'octaves': 2}},
         [_dist(0.95, 0.9), _reverb(3.0, 0.55), _filt('lowpass', 280, 1.4)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'Bb1','Bb1','Bb1',_N,'A1','A1','A1'],
         sidechain='deep'),
]

# ---------------------------------------------------------------------------
# BASSES — the distorted offbeat alternative: one hit on the 3rd 16th of each
# beat (or the offbeat and the 16th after it), dry and crushed. Never on the
# kick.
# ---------------------------------------------------------------------------
_BASSES = [
    # Distorted offbeat saw
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.1, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.1, 'release': 0.06,
                             'baseFrequency': 90, 'octaves': 3}},
         [_dist(0.85, 0.75), _filt('lowpass', 700, 2)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N]),
    # Offbeat square with octave jumps and a sweeping filter
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.1, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.1, 'release': 0.05,
                             'baseFrequency': 90, 'octaves': 3}},
         [_dist(0.8, 0.7), _filt('lowpass', 900, 1.5)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A2',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N,_N,_N,'A2',_N],
         automation=[_auto('effect:1:frequency', 400, 1400, 'tri')]),
    # Detuned offbeat — two saws beating against each other under the distortion
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 2, 'spread': 25},
          'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.15, 'release': 0.08},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.15, 'release': 0.08,
                             'baseFrequency': 80, 'octaves': 2.5}},
         [_dist(0.85, 0.8), _filt('lowpass', 600, 1.5)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'C2',_N]),
    # Off-kick pairs: the offbeat and the 16th after it
    _cfg('bass', 'bass', -9, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.07, 'sustain': 0.05, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.05, 'release': 0.04,
                             'baseFrequency': 100, 'octaves': 3}},
         [_dist(0.9, 0.8), _filt('lowpass', 800, 2)],
         [_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',
          _N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'G1','A1']),
]

# ---------------------------------------------------------------------------
# CLAPS — beats 2 & 4, distorted. Low probability: hard techno is mostly kick,
# rumble and hats, and a constant clap softens it.
# ---------------------------------------------------------------------------
_CLAPS = [
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.05}},
         [_dist(0.6, 0.5), _filt('bandpass', 1800, 0.8), _reverb(0.8, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.055}},
         [_dist(0.75, 0.6), _filt('highpass', 900, 0.7)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Big warehouse clap
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0, 'release': 0.08}},
         [_dist(0.5, 0.4), _reverb(2.0, 0.4)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# CLOSED HATS — fast, bright 16ths, often distorted for the gritty top end.
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01},
          'harmonicity': 5.0, 'modulationIndex': 35, 'resonance': 5000, 'octaves': 1.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 580, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.6},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Distorted 16ths — peak-time grit
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.012},
          'harmonicity': 5.8, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.7},
         [_dist(0.4, 0.35)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 16ths leaving the offbeat to the open hat
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 620, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 7000, 'octaves': 1.8},
         [],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4',
          'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4']),
    # Distorted, with holes for drive
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012},
          'harmonicity': 7.0, 'modulationIndex': 50, 'resonance': 7500, 'octaves': 1.9},
         [_dist(0.5, 0.45)],
         ['C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4',_N,'C4','C4',
          'C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4']),
    # Noise 16ths, highpassed hard
    _cfg('hihat', 'hihat', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.022, 'sustain': 0, 'release': 0.01}},
         [_dist(0.3, 0.3), _filt('highpass', 8500, 0.8)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
]

# ---------------------------------------------------------------------------
# OPEN HATS — offbeat open hats over the 16ths, harder and brighter than in
# techno, some distorted.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    _cfg('open_hat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.2, 'release': 0.08},
          'harmonicity': 5.5, 'modulationIndex': 38, 'resonance': 5500, 'octaves': 1.6},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('open_hat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.16, 'release': 0.06},
          'harmonicity': 7.0, 'modulationIndex': 50, 'resonance': 7500, 'octaves': 1.9},
         [_dist(0.5, 0.4)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('open_hat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.1}},
         [_dist(0.4, 0.35), _filt('highpass', 7000, 1)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('open_hat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 560, 'envelope': {'attack': 0.001, 'decay': 0.26, 'release': 0.12},
          'harmonicity': 6.0, 'modulationIndex': 44, 'resonance': 6500, 'octaves': 1.7},
         [_reverb(0.9, 0.18)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# PERCUSSION — industrial: anvil clangs, crushed noise snaps, distorted toms,
# metal ticks. Zero to two per track, each with its own id.
# ---------------------------------------------------------------------------
_PERCS = [
    # Anvil clang
    _cfg('anvil', 'perc', -15, '16n', 'MetalSynth',
         {'frequency': 220, 'envelope': {'attack': 0.001, 'decay': 0.15, 'release': 0.06},
          'harmonicity': 3.7, 'modulationIndex': 24, 'resonance': 2600, 'octaves': 1.0},
         [_dist(0.7, 0.6), _reverb(1.2, 0.3)],
         [_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,
          _N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N]),
    # Crushed noise snaps
    _cfg('noise_snap', 'perc', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [_dist(0.85, 0.7), _filt('bandpass', 2200, 1.5)],
         [_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,
          _N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,_N]),
    # Warehouse metal hit — a big reverb tail across the bar
    _cfg('metal_hit', 'perc', -17, '16n', 'MetalSynth',
         {'frequency': 140, 'envelope': {'attack': 0.001, 'decay': 0.25, 'release': 0.1},
          'harmonicity': 2.9, 'modulationIndex': 20, 'resonance': 2000, 'octaves': 1.2},
         [_filt('highpass', 600, 0.7), _reverb(2.5, 0.45)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N]),
    # Distorted tom loop
    _cfg('toms', 'perc', -14, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.06}},
         [_dist(0.8, 0.6)],
         [_N,_N,_N,'D3',_N,_N,'D3',_N,_N,_N,_N,'A2',_N,_N,_N,_N,
          _N,_N,_N,'D3',_N,_N,'D3',_N,_N,_N,_N,'A2',_N,_N,'F2',_N]),
    # Metal ticks on the last 16th of each beat
    _cfg('ticks', 'perc', -19, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008},
          'harmonicity': 8.0, 'modulationIndex': 40, 'resonance': 9000, 'octaves': 1.5},
         [_dist(0.5, 0.4)],
         [_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',
          _N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4']),
]

# ---------------------------------------------------------------------------
# LEADS — screeching hoovers and acid screeches over the top. They may cross
# the kick: they are the riff, not the low end. Hoover and acid lines are
# written with consecutive notes so _slides has something to glide between.
# ---------------------------------------------------------------------------
_LEADS = [
    # Hoover riff — detuned saws, chorus, pitch glides between notes
    _cfg('hoover', 'lead', -15, '8n', 'Synth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 45},
          'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.6, 'release': 0.25}},
         [_chorus(2, 3.5, 0.8, 0.5), _dist(0.5, 0.45), _filt('lowpass', 2800, 1.2), _reverb(1.8, 0.25)],
         ['A3',_N,_N,'A3',_N,_N,'G3','A3',_N,_N,'C4',_N,'A3',_N,_N,_N,
          'A3',_N,_N,'A3',_N,_N,'G3','A3',_N,'E3','G3',_N,'A3',_N,_N,_N]),
    # Screaming hoover — long, high notes swooping up into the next
    _cfg('hoover', 'lead', -17, '4n', 'Synth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 60},
          'envelope': {'attack': 0.05, 'decay': 0.4, 'sustain': 0.7, 'release': 0.4}},
         [_chorus(1.5, 4, 0.9, 0.6), _dist(0.6, 0.5), _filt('lowpass', 3200, 1), _reverb(2.5, 0.3)],
         ['A4',_N,_N,_N,_N,_N,'G4','A4',_N,_N,_N,_N,_N,_N,_N,_N,
          'A4',_N,_N,_N,_N,_N,'C5','A4',_N,_N,_N,_N,'E4','G4',_N,_N],
         entry_loop=2),
    # Acid screech — resonant saw high up, across the kick
    _cfg('acid', 'lead', -16, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'Q': 9, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.1, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.1, 'release': 0.05,
                             'baseFrequency': 400, 'octaves': 4}},
         [_dist(0.75, 0.6), _filt('lowpass', 2000, 6), _filt('highpass', 250, 0.7)],
         ['A3',_N,'A3','A4',_N,'A3','G3',_N,'A3','C4',_N,'A3',_N,'A4','A3',_N,
          'A3',_N,'A3','A4',_N,'A3','D4','C4',_N,'A3',_N,'G3','A3',_N,'E4',_N],
         automation=[_auto('effect:1:frequency', 800, 5000, 'tri')]),
    # Industrial FM screech on the off-16ths
    _cfg('screech', 'lead', -19, '16n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 22,
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.3, 'release': 0.05}},
         [_dist(0.7, 0.5), _filt('highpass', 500, 0.7), _delay('8n.', 0.3, 0.2)],
         [_N,_N,'A4','A4',_N,_N,'A4',_N,_N,_N,'A4','A4',_N,_N,'G4',_N,
          _N,_N,'A4','A4',_N,_N,'A4',_N,_N,_N,'C5','A4',_N,_N,'G4',_N]),
    # Distorted rave stab — a hollow fifth
    _cfg('rave_stab', 'lead', -16, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_dist(0.85, 0.7), _filt('bandpass', 1500, 1.2), _reverb(1.0, 0.2)],
         [_N,_N,_N,'A3,E4',_N,_N,_N,_N,_N,_N,'A3,E4',_N,_N,_N,_N,_N,
          _N,_N,_N,'A3,E4',_N,_N,_N,_N,_N,_N,'A3,E4',_N,_N,_N,'G3,D4',_N]),
    # Siren — a swept saw that rises and falls over the loop
    _cfg('siren', 'lead', -17, '1m', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.6, 'release': 0.5}},
         [_dist(0.5, 0.55), _filt('lowpass', 1500, 4), _delay('8n', 0.3, 0.2)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 500, 3500, 'tri')],
         entry_loop=4),
]

# Glide probability per lead id — hoovers bend into most notes, acid slides on some.
_LEAD_SLIDE_PROB = {'hoover': 0.6, 'acid': 0.3}

# ---------------------------------------------------------------------------
# FILLS — phrase markers gated by loop_modulo (each loop = 2 bars).
# ---------------------------------------------------------------------------
_FILLS = [
    # Distorted snare roll over the last beat, every 16 bars
    _cfg('fill_roll', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03}},
         [_dist(0.6, 0.5), _reverb(0.6, 0.3)],
         [_N]*24 + ['C2', _N, 'C2', _N, 'C2', 'C2', 'C2', 'C2'],
         loop_modulo=8, loop_modulo_remainder=7),
    # Noise riser into the next phrase, every 8 bars
    _cfg('fill_swell', 'perc', -17, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.5, 'decay': 0.1, 'sustain': 0.9, 'release': 0.2}},
         [_filt('highpass', 2000, 1), _reverb(2.0, 0.5)],
         ['C3'] + [_N]*31,
         loop_modulo=4, loop_modulo_remainder=3),
]


class HardTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HARD_TECHNO
    BPM_RANGE = (145, 155)
    LEVEL_DB = -7.7
    KEY_ROLES = ('kick', 'bass')
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.35

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        # The rolling rumble is the modern hard techno sound; the offbeat bass is the older style.
        bass = copy.deepcopy(cls._pick(_RUMBLES if random.random() < 0.6 else _BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))

        _clear_kick_steps(bass, kick)
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        if bass['id'] == 'rumble':
            bass['pattern']['velocities'] = _vel_rumble(bass['pattern']['steps'])
        else:
            bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.25, ghost_prob=0.05)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])

        layers = [kick, bass, hihat]

        open_hat = cls._maybe(_OPEN_HATS, 0.8)
        if open_hat:
            open_hat = copy.deepcopy(open_hat)
            open_hat['pattern']['velocities'] = _vel(open_hat['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
            layers.append(open_hat)

        clap = cls._maybe(_CLAPS, 0.25)
        if clap:
            clap = copy.deepcopy(clap)
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        for perc in random.sample(_PERCS, random.choice([0, 1, 1, 2])):
            perc = copy.deepcopy(perc)
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.3, ghost_prob=0.08)
            layers.append(perc)

        lead = cls._maybe(_LEADS, 0.7)
        if lead:
            lead = copy.deepcopy(lead)
            steps = lead['pattern']['steps']
            lead['pattern']['velocities'] = _vel(steps, accent_prob=0.3, ghost_prob=0.0)
            slide_prob = _LEAD_SLIDE_PROB.get(lead['id'])
            if slide_prob is not None:
                lead['pattern']['slides'] = _slides(steps, slide_prob)
            if 'entry_loop' not in lead and random.random() < 0.4:
                lead['entry_loop'] = 2
            layers.append(lead)

        fill = cls._maybe(_FILLS, 0.45)
        if fill:
            layers.append(copy.deepcopy(fill))

        root_pc = cls._apply_key_coherence(layers)
        _tune_kick(kick, root_pc, _KICK_LOWEST_MIDI)
        return layers

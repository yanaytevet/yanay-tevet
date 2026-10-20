import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _reverb, _delay, _filt,
    _vel, _vel_groove, _vel_kick,
)

# ---------------------------------------------------------------------------
# KICKS — clean, round four-on-the-floor. No distortion: minimal's kick is a
# soft, rounded thud that leaves the high end to the micro-percussion. Every
# entry hits all eight quarters; two add a single 16th pickup before a downbeat.
# Basses must stay off steps 15 and 31 because of those pickups.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Tighter and shorter — more room between hits
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 5, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.7}},
         [],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,
          'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N]),
    # Soft and long with a touch of room
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.0}},
         [_reverb(0.4, 0.06)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Ghost pickup into the loop restart
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0.01, 'release': 0.85}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Slightly clickier top, still clean
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.75}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Ghost pickup into bar 2
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HATS — sparse, short and quiet. Minimal never runs a wall of 16ths; a few
# offbeat ticks are enough, and the generator lets them drop out for whole
# loops so the groove breathes.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Plain offbeat 8ths
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 7.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.8},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Only the offbeats of 2 and 4
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 720, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.012}, 'harmonicity': 7.8, 'modulationIndex': 44, 'resonance': 6000, 'octaves': 1.9},
         [],
         [_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,
          _N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N]),
    # Skippy — offbeats with a late 16th here and there
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.007}, 'harmonicity': 9.0, 'modulationIndex': 50, 'resonance': 7000, 'octaves': 2.1},
         [],
         [_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Late 16th ticks only — almost subliminal
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.006}, 'harmonicity': 9.5, 'modulationIndex': 55, 'resonance': 8000, 'octaves': 2.2},
         [],
         [_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,
          _N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N]),
    # Half-open hat on every other offbeat
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 560, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.03}, 'harmonicity': 6.5, 'modulationIndex': 38, 'resonance': 4500, 'octaves': 1.7},
         [],
         [_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,
          _N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N]),
    # 16th pairs on the offbeats
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 760, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.008}, 'harmonicity': 8.4, 'modulationIndex': 48, 'resonance': 6800, 'octaves': 2.0},
         [],
         [_N,_N,'C4','C4',_N,_N,_N,_N,_N,_N,'C4','C4',_N,_N,_N,_N,
          _N,_N,'C4','C4',_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# PERCUSSION — the identity of minimal. Tiny, dry, precisely placed hits —
# rims, toks, clicks, snaps — each playing only a handful of notes per loop,
# often off the grid's obvious spots, with silence doing as much work as the
# hits. Every track has one of these; panning spreads them into small details.
# ---------------------------------------------------------------------------
_PERCS = [
    # Woody rim "tok", syncopated, with a short echo trail
    _cfg('rim', 'perc', -12, '32n', 'MembraneSynth',
         {'pitchDecay': 0.006, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03}},
         [_delay('8n.', 0.22, 0.14)],
         [_N,_N,_N,'E5',_N,_N,_N,_N,_N,_N,'E5',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'E5',_N,_N,_N,_N,'E5',_N,_N,_N,_N],
         pan=0.2),
    # Dry noise click, highpassed to a pin-prick
    _cfg('click', 'perc', -14, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.012, 'sustain': 0, 'release': 0.006}},
         [_filt('highpass', 4500, 1)],
         [_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,
          _N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4','C4',_N],
         pan=0.3),
    # Two dub rims; the long echo builds the rest of the pattern
    _cfg('rim_dub', 'perc', -13, '32n', 'MembraneSynth',
         {'pitchDecay': 0.005, 'octaves': 2.2, 'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.03}},
         [_delay('8n.', 0.45, 0.32), _filt('highpass', 400, 0.7)],
         [_N,_N,_N,_N,_N,_N,'G5',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,'G5',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         pan=-0.25),
    # Low tok — a muted conga feel
    _cfg('tok', 'perc', -11, '16n', 'MembraneSynth',
         {'pitchDecay': 0.01, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,'C4',_N,
          _N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,'G4',_N],
         pan=-0.2),
    # Finger snap on beat 4 only, with a little room
    _cfg('snap', 'perc', -12, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.03}},
         [_filt('bandpass', 1900, 2), _reverb(0.9, 0.22)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,'C4']),
    # Metallic tick on the second 16th of a few beats — the off-grid nudge
    _cfg('tick', 'perc', -16, '32n', 'MetalSynth',
         {'frequency': 1800, 'envelope': {'attack': 0.001, 'decay': 0.008, 'release': 0.004}, 'harmonicity': 1.4, 'modulationIndex': 12, 'resonance': 5000, 'octaves': 0.8},
         [],
         [_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,
          _N,_N,'C4',_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N],
         pan=-0.35),
    # Two-pitch wood blocks in call and response
    _cfg('block', 'perc', -13, '32n', 'MembraneSynth',
         {'pitchDecay': 0.004, 'octaves': 1.5, 'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.02}},
         [],
         [_N,_N,_N,'A5',_N,_N,_N,'D5',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,'D5','A5',_N,_N,_N,_N],
         pan=0.25),
    # Rimshot on 2 and 4 — the only "backbeat" minimal usually has
    _cfg('rim_backbeat', 'perc', -14, '32n', 'MembraneSynth',
         {'pitchDecay': 0.005, 'octaves': 2.5, 'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 600, 0.7), _reverb(0.5, 0.12)],
         [_N,_N,_N,_N,'F5',_N,_N,_N,_N,_N,_N,_N,'F5',_N,_N,_N,
          _N,_N,_N,_N,'F5',_N,_N,_N,_N,_N,_N,_N,'F5',_N,'F5',_N]),
]

# ---------------------------------------------------------------------------
# MICRO TEXTURE — an optional second percussion layer even quieter than the
# first: shaker grains, ticks and crackle panned wide, dropping in and out.
# ---------------------------------------------------------------------------
_MICRO_PERCS = [
    # Shaker grains with holes
    _cfg('shaker', 'perc', -21, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.025, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 6500, 0.7)],
         [_N,'C4','C4',_N,_N,'C4',_N,'C4',_N,'C4','C4',_N,_N,_N,_N,'C4',
          _N,'C4','C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N],
         pan=0.4),
    # Scattered metal ticks
    _cfg('ticks', 'perc', -20, '32n', 'MetalSynth',
         {'frequency': 2400, 'envelope': {'attack': 0.001, 'decay': 0.005, 'release': 0.003}, 'harmonicity': 2.1, 'modulationIndex': 20, 'resonance': 8000, 'octaves': 1.0},
         [],
         [_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4','C4',_N,
          _N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,'C4'],
         pan=-0.45),
    # Vinyl-like crackle, almost random placement
    _cfg('crackle', 'perc', -22, '32n', 'NoiseSynth',
         {'noise': {'type': 'brown'}, 'envelope': {'attack': 0.001, 'decay': 0.006, 'sustain': 0, 'release': 0.004}},
         [_filt('highpass', 3000, 0.7)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,
          _N,'C4',_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N],
         pan=0.5),
    # Bandpassed noise "tsk" a 16th after a few beats
    _cfg('tsk', 'perc', -20, '32n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('bandpass', 5000, 3)],
         [_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,
          _N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         pan=-0.3),
]

# ---------------------------------------------------------------------------
# BASS — sparse, short and round, a few single notes on the 3rd or 4th 16th of
# some beats so they sit in the holes the kick leaves. Never on a kick step
# (including the 15/31 pickups some kicks add). Sine, triangle, FM "plonk" and
# a pitched-drum "boing" give the clicky-round minimal bass palette.
# ---------------------------------------------------------------------------
_BASSES = [
    # A — sine pluck with a quick filter click on top
    _cfg('bass', 'bass', -2, '16n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0.0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 160, 'octaves': 2.5}},
         [],
         [_N,_N,_N,'A1',_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,
          _N,_N,_N,'A1',_N,_N,'G1',_N,_N,_N,_N,'A1',_N,_N,_N,_N]),
    # D — pitched-drum "boing", the dubby minimal bass
    _cfg('bass', 'bass', -1, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 0.8, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.0, 'release': 0.06}},
         [],
         [_N,_N,'D2',_N,_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,_N,_N,
          _N,_N,'D2',_N,_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,'F2',_N]),
    # E — FM plonk, woody attack
    _cfg('bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 1, 'modulationIndex': 4, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.0, 'release': 0.05},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.02}},
         [_filt('lowpass', 900, 1)],
         [_N,_N,_N,'E2',_N,_N,'E2',_N,_N,_N,_N,'G2',_N,_N,_N,_N,
          _N,_N,_N,'E2',_N,_N,'E2',_N,_N,_N,_N,'D2',_N,_N,_N,_N]),
    # G — square through a low lowpass: round body, clicky edge
    _cfg('bass', 'bass', -3, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0.0, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 110, 'octaves': 2.2}},
         [_filt('lowpass', 600, 1)],
         [_N,_N,'G1',_N,_N,_N,_N,'G1',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'G1',_N,_N,_N,_N,'G1',_N,_N,'Bb1',_N,_N,_N,'G1',_N]),
    # C — triangle, a little more talkative
    _cfg('bass', 'bass', -2, '16n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.0, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 180, 'octaves': 2.0}},
         [],
         [_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,
          _N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'Bb1',_N,_N,'C2',_N]),
    # A — three notes and an octave flick; mostly silence
    _cfg('bass', 'bass', -1, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.0, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.04, 'baseFrequency': 200, 'octaves': 1.5}},
         [],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,'A1',_N,_N,_N,'A2',_N,_N,_N,_N]),
    # F — FM dub bass with a slight echo
    _cfg('bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 3, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.0, 'release': 0.06},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.03}},
         [_filt('lowpass', 700, 1), _delay('8n.', 0.18, 0.1)],
         [_N,_N,'F1',_N,_N,_N,'F1',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'F1',_N,_N,_N,_N,_N,_N,_N,'Ab1',_N,_N,_N,'F1',_N]),
]

# ---------------------------------------------------------------------------
# DUB STABS — optional, rare, late. One chord or blip a bar fed into a long
# echo, the Chain Reaction / Villalobos move. Few hits, lots of tail.
# ---------------------------------------------------------------------------
_STABS = [
    # Minor-seventh dub chord
    _cfg('stab', 'stab', -17, '16n', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.0, 'release': 0.1}},
         [_filt('lowpass', 1400, 1.5), _delay('8n.', 0.5, 0.35), _reverb(2.0, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3,C4,E4,G4',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3,C4,E4,G4',_N,_N,_N,_N]),
    # Hollow sus chord, square
    _cfg('stab', 'stab', -18, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.0, 'release': 0.08}},
         [_filt('lowpass', 1200, 1.2), _delay('4n', 0.45, 0.3)],
         [_N,_N,_N,_N,_N,_N,'D4,G4,A4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Single sine blip; the 8th echo turns two notes into a figure
    _cfg('stab', 'stab', -16, '32n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.04}},
         [_delay('8n', 0.4, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,'A5',_N,_N,_N,_N,_N,_N,'E5',_N]),
    # FM bell blip
    _cfg('stab', 'stab', -17, '32n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 8, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.0, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.05}},
         [_delay('8n.', 0.42, 0.28), _reverb(2.5, 0.3)],
         [_N,_N,_N,_N,_N,_N,'A4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A4',_N,_N,_N,_N,_N]),
]


class MinimalTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.MINIMAL_TECHNO
    BPM_RANGE = (124, 130)
    LEVEL_DB = -1.9
    PROFILE = GenreProfile(
        drums='Clean, round four-on-the-floor kick; sparse hi-hats that drop in and out',
        bass='Sparse, short, round notes in the gaps',
        signature='Tiny clicks, rims, blips and toks, with lots of silence',
        mood='Restrained, spacious, hypnotic',
        key_trait='drums',
        kick_pattern='four',
        bass_pattern='sparse',
    )
    KEY_ROLES = ('perc', 'hihat')
    SIDECHAIN_DEPTH = 0.6
    SIDECHAIN_RELEASE = 0.4

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        perc = copy.deepcopy(cls._pick(_PERCS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        # Wide accent/ghost spread: dynamics are what make so few hits feel alive.
        perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.3, ghost_prob=0.2)
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.1)

        if random.random() < 0.5:
            hihat['dropout_prob'] = random.choice([0.2, 0.3, 0.4])

        layers = [kick, hihat, perc, bass]

        if random.random() < 0.6:
            micro = copy.deepcopy(cls._pick(_MICRO_PERCS))
            micro['pattern']['velocities'] = _vel(micro['pattern']['steps'], accent_prob=0.2, ghost_prob=0.3)
            micro['dropout_prob'] = random.choice([0.25, 0.35, 0.45])
            layers.append(micro)

        if random.random() < 0.35:
            stab = copy.deepcopy(cls._pick(_STABS))
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
            # Arrives late and comes and goes, so it reads as a detail rather than a hook.
            stab['entry_loop'] = random.choice([1, 2])
            stab['dropout_prob'] = 0.3
            layers.append(stab)

        cls._apply_key_coherence(layers)
        return layers

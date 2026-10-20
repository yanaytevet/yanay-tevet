import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus, _filt, _delay, _auto, _slides, _vel,
    _vel_groove, _vel_kick, _clear_kick_steps, _tune_kick, _vel_rumble,
)

# F1 (44 Hz) up to E2 (82 Hz): tuned higher than hard techno, so the kick is a boxy "bonk" that
# cuts through a rented rig rather than a deep tail.
_KICK_LOWEST_MIDI = 29

# ---------------------------------------------------------------------------
# KICKS — free-party tekno: a short, boxy kick driven into the ground and
# filtered like it went through cheap gear. Short decay (no hard techno tail),
# extreme distortion, lowpassed — lo-fi rather than polished. Relentless: every
# quarter, some entries with 16ths rolling into the downbeat. The note is a
# placeholder; _tune_kick retunes it to the track root.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.4}},
         [_dist(0.95, 0.9), _filt('lowpass', 3000, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Thin and boxy — sub cut, top cut: the sound of a blown rig
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.35}},
         [_dist(1.0, 0.95), _filt('highpass', 45, 0.7), _filt('lowpass', 2200, 0.9)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Double distortion fizz
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0.01, 'release': 0.4}},
         [_dist(0.9, 0.9), _dist(0.6, 0.5), _filt('lowpass', 4000, 0.7)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Short, hard punch
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.9, 0.85), _filt('lowpass', 4500, 0.7)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Distorted 909 in a small room
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.45}},
         [_dist(0.85, 0.85), _reverb(0.4, 0.08)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Extra 16th into each bar's downbeat
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0.01, 'release': 0.35}},
         [_dist(0.95, 0.9), _filt('lowpass', 3200, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Two 16ths rolling into the loop restart
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.3}},
         [_dist(0.95, 0.9), _filt('lowpass', 3500, 0.8)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1','C1']),
]

# ---------------------------------------------------------------------------
# BASSES — dry and crushed, no reverb (that is hard techno's polish): the
# distorted offbeat bass, or staccato rolls in the gaps between kicks. Role
# 'bass', never on the kick — lines that cross the kick live in _ACIDS.
# ---------------------------------------------------------------------------
_BASSES = [
    # Distorted offbeat square
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.15, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.15, 'release': 0.05,
                             'baseFrequency': 100, 'octaves': 3}},
         [_dist(0.9, 0.8), _filt('lowpass', 1200, 1)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N]),
    # Offbeat saw jumping octaves
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.09, 'sustain': 0.1, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.1, 'release': 0.05,
                             'baseFrequency': 110, 'octaves': 3}},
         [_dist(0.85, 0.75), _filt('lowpass', 1400, 1)],
         [_N,_N,'A1',_N,_N,_N,'A2',_N,_N,_N,'A1',_N,_N,_N,'A2',_N,
          _N,_N,'A1',_N,_N,_N,'A2',_N,_N,_N,'G1',_N,_N,_N,'G2',_N]),
    # Offbeat FM "bwom", crushed
    _cfg('bass', 'bass', -7, '16n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8,
          'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_dist(0.8, 0.7), _filt('lowpass', 900, 1.5)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'C2',_N]),
    # Machine-gun roll: three staccato 16ths after every kick, bone dry
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03,
                             'baseFrequency': 120, 'octaves': 3}},
         [_dist(0.9, 0.8), _filt('lowpass', 700, 2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'G1','G1','G1']),
    # Bouncing off-kick 16ths: the 2nd and 4th 16th of each beat
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.05, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.05, 'release': 0.04,
                             'baseFrequency': 110, 'octaves': 3.5}},
         [_dist(0.85, 0.8), _filt('lowpass', 1000, 1.5)],
         [_N,'A1',_N,'A1',_N,'A1',_N,'A1',_N,'A1',_N,'A2',_N,'A1',_N,'A1',
          _N,'A1',_N,'A1',_N,'A1',_N,'A2',_N,'G1',_N,'G1',_N,'A1',_N,'C2']),
    # Offbeat pairs — "da-da" after each kick's gap
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.05, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.05, 'release': 0.04,
                             'baseFrequency': 100, 'octaves': 3}},
         [_dist(0.95, 0.85), _filt('lowpass', 800, 1.5)],
         [_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A2',
          _N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'C2','A1',_N,_N,'G1','A1']),
    # Distorted tuned-tom bass rolling between kicks
    _cfg('bass', 'bass', -6, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_dist(0.85, 0.8), _filt('lowpass', 900, 1)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','C2',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','G1','A1',_N,'C2','A1','A1']),
]

# ---------------------------------------------------------------------------
# ACIDS — the squelching 303-style line that free-party tekno is famous for.
# Role 'lead': it runs straight across the kick, an octave above the bass.
# Resonant, driven, with slides assigned per track and a cutoff sweep.
# ---------------------------------------------------------------------------
_ACIDS = [
    _cfg('acid', 'lead', -13, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'Q': 10, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.1, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.05, 'release': 0.04,
                             'baseFrequency': 220, 'octaves': 4.5}},
         [_dist(0.8, 0.6), _filt('lowpass', 2500, 3)],
         ['A2','A2',_N,'A3','A2',_N,'C3','A2',_N,'A2','G2',_N,'A2','A3',_N,'A2',
          'A2',_N,'A2','C3',_N,'A2','D3','C3','A2',_N,'A3',_N,'G2','A2',_N,'E2'],
         automation=[_auto('effect:1:frequency', 600, 4500, 'tri')]),
    _cfg('acid', 'lead', -14, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'filter': {'Q': 12, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.1, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0.05, 'release': 0.05,
                             'baseFrequency': 200, 'octaves': 5}},
         [_dist(0.85, 0.65), _filt('lowpass', 2200, 4)],
         ['G2','G3','G2',_N,'G2','Bb2',_N,'G2','G3',_N,'G2','F3',_N,'G2','G2','D3',
          'G2','G3','G2',_N,'G2','Bb2','C3',_N,'G3','G2',_N,'F3','G2',_N,'Bb2','G2'],
         automation=[_auto('effect:1:frequency', 500, 4000, 'tri')]),
    # Phrygian acid — the half step above the root is the dark free-party colour
    _cfg('acid', 'lead', -13, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'Q': 11, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.1, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.05, 'release': 0.04,
                             'baseFrequency': 250, 'octaves': 4}},
         [_dist(0.9, 0.7), _filt('lowpass', 2800, 3), _delay('8n.', 0.3, 0.15)],
         ['A2',_N,'A3','A2','Bb2',_N,'A2','A3',_N,'A2','C3',_N,'A2','A2','G3',_N,
          'A2',_N,'A3','A2','Bb2','A2',_N,'E3',_N,'A2','C3','A2',_N,'G2','A2',_N],
         automation=[_auto('effect:1:frequency', 700, 5000, 'ramp')]),
    _cfg('acid', 'lead', -14, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'Q': 9, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0.15, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0.1, 'release': 0.05,
                             'baseFrequency': 180, 'octaves': 5}},
         [_dist(0.75, 0.6), _filt('lowpass', 2000, 3)],
         ['C3','C3',_N,'C3','Eb3',_N,'C3','C4',_N,'C3',_N,'Bb2','C3',_N,'G3',_N,
          'C3','C3',_N,'C3','Eb3','F3',_N,'C3','C4',_N,'C3','Bb2',_N,'C3',_N,'G2'],
         automation=[_auto('effect:1:frequency', 500, 4200, 'tri')]),
    # Sparse squelch — fewer, longer notes so each filter blip is heard
    _cfg('acid', 'lead', -13, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'filter': {'Q': 14, 'type': 'lowpass', 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.15, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.05, 'release': 0.06,
                             'baseFrequency': 240, 'octaves': 4.5}},
         [_dist(0.85, 0.65), _filt('lowpass', 2600, 3)],
         ['A2',_N,_N,'A2',_N,_N,'A3',_N,'A2',_N,'C3','A2',_N,_N,'E3',_N,
          'A2',_N,_N,'A2',_N,_N,'A3','G3',_N,'A2',_N,_N,'C3',_N,'A2',_N],
         automation=[_auto('effect:1:frequency', 600, 4800, 'tri')]),
]

# ---------------------------------------------------------------------------
# STABS — sparse, sampled-sounding hits: a crushed rave chord, a hoover stab,
# an orchestra-style hit, a telephone-filtered blip. Band-limited and driven so
# they sound like they came off a cheap sampler, not a polished synth.
# ---------------------------------------------------------------------------
_STABS = [
    # Lo-fi rave chord stab
    _cfg('rave_stab', 'stab', -17, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_dist(0.8, 0.6), _filt('bandpass', 1600, 0.9), _delay('8n', 0.3, 0.2)],
         [_N,_N,_N,_N,_N,_N,'A3,C4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'A3,C4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Hoover stab
    _cfg('hoover_stab', 'stab', -16, '8n', 'Synth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 50},
          'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.2, 'release': 0.1}},
         [_chorus(2, 3, 0.8, 0.5), _dist(0.6, 0.5), _filt('bandpass', 1200, 0.8)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N]),
    # Orchestra-style hit, once per loop
    _cfg('orch_hit', 'stab', -17, '8n', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.3, 'sustain': 0, 'release': 0.2}},
         [_dist(0.5, 0.4), _filt('lowpass', 3000, 1), _reverb(1.5, 0.25)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A2,E3,A3,C4',_N,_N,_N]),
    # Telephone blip in a dotted-8th delay
    _cfg('blip', 'stab', -18, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 6,
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.04}},
         [_filt('bandpass', 1800, 3), _dist(0.6, 0.4), _delay('8n.', 0.45, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A4',_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A4',_N]),
    # Metallic AM stab, crushed
    _cfg('metal_stab', 'stab', -17, '16n', 'AMSynth',
         {'harmonicity': 2.5,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.06}},
         [_dist(0.85, 0.6), _filt('bandpass', 1400, 1.2)],
         [_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# PERCUSSION — metallic and raw: crushed noise snares, distorted clangs, tin
# cans, toms. One or two per track, each with its own id.
# ---------------------------------------------------------------------------
_PERCS = [
    # Crushed noise snare on 2 & 4 with pickups
    _cfg('noise_snare', 'perc', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.1}},
         [_dist(0.8, 0.7)],
         [_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',
          _N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3']),
    # Distorted metal clang, syncopated
    _cfg('clang', 'perc', -10, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.02},
          'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 4000, 'octaves': 1.5},
         [_dist(0.7, 0.65)],
         [_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,'C3',
          _N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N,'C3']),
    # Pink noise bursts
    _cfg('noise_burst', 'perc', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.08}},
         [_dist(0.75, 0.6), _reverb(0.3, 0.15)],
         ['C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,
          'C3',_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N,_N]),
    # Crushed rimshot "tok"
    _cfg('rimshot', 'perc', -12, '16n', 'MembraneSynth',
         {'pitchDecay': 0.006, 'octaves': 1.5, 'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.02}},
         [_dist(0.7, 0.5), _filt('highpass', 400, 0.7)],
         [_N,_N,_N,'B4',_N,_N,'B4',_N,_N,_N,_N,'B4',_N,_N,_N,_N,
          _N,_N,_N,'B4',_N,_N,'B4',_N,_N,'B4',_N,'B4',_N,_N,_N,_N]),
    # Distorted toms
    _cfg('toms', 'perc', -12, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.05}},
         [_dist(0.85, 0.7)],
         [_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,
          _N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,'C3',_N,_N,'A2','A2',_N]),
    # Tin can on the last 16th of each beat, lowpassed like a cheap sample
    _cfg('tin', 'perc', -14, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.03},
          'harmonicity': 1.2, 'modulationIndex': 8, 'resonance': 1800, 'octaves': 0.4},
         [_dist(0.6, 0.5), _filt('lowpass', 4000, 1)],
         [_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',
          _N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,'C4','C4']),
]

# ---------------------------------------------------------------------------
# CLOSED HATS — raw 16ths, often distorted and lowpassed (lo-fi rather than
# hard techno's bright sizzle).
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 7.0, 'modulationIndex': 50, 'resonance': 6500, 'octaves': 1.8},
         [_dist(0.6, 0.5), _filt('lowpass', 7000, 0.7)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01},
          'harmonicity': 8.0, 'modulationIndex': 55, 'resonance': 7000, 'octaves': 2.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Leaves the offbeat for the open hat
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01},
          'harmonicity': 7.5, 'modulationIndex': 52, 'resonance': 6800, 'octaves': 1.9},
         [_dist(0.5, 0.45)],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4',
          'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4']),
    # Lo-fi noise 16ths, band-limited like an 8-bit sample
    _cfg('hihat', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01}},
         [_dist(0.5, 0.4), _filt('bandpass', 5000, 1.2)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Irregular, distorted
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015},
          'harmonicity': 8.5, 'modulationIndex': 58, 'resonance': 8000, 'octaves': 2.0},
         [_dist(0.55, 0.5)],
         ['C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4','C4',_N,'C4',_N,'C4',
          'C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4']),
    # Galloping, three on one off
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 820, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 8.0, 'modulationIndex': 56, 'resonance': 7500, 'octaves': 2.1},
         [_dist(0.45, 0.45), _filt('lowpass', 6500, 0.7)],
         ['C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,
          'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4','C4']),
]

# ---------------------------------------------------------------------------
# OPEN HATS — offbeat, crushed and short. Optional: plenty of tekno runs on
# closed hats and percussion alone.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    _cfg('open_hat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_dist(0.7, 0.6), _filt('highpass', 5000, 1)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('open_hat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.14, 'release': 0.06},
          'harmonicity': 6.5, 'modulationIndex': 45, 'resonance': 6000, 'octaves': 1.7},
         [_dist(0.6, 0.5), _filt('lowpass', 7500, 0.7)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('open_hat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 720, 'envelope': {'attack': 0.001, 'decay': 0.1, 'release': 0.05},
          'harmonicity': 7.5, 'modulationIndex': 52, 'resonance': 7000, 'octaves': 1.9},
         [_dist(0.8, 0.6)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# FILLS — phrase markers gated by loop_modulo (each loop = 2 bars). The
# accelerating snare roll is a free-party staple.
# ---------------------------------------------------------------------------
_FILLS = [
    # Crushed snare roll across the last bar, every 8 bars
    _cfg('fill_roll', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03}},
         [_dist(0.8, 0.6)],
         [_N]*16 + ['C2', _N, _N, _N, 'C2', _N, 'C2', _N, 'C2', _N, 'C2', 'C2', 'C2', 'C2', 'C2', 'C2'],
         loop_modulo=4, loop_modulo_remainder=3),
    # Distorted tom run down into the next phrase, every 16 bars
    _cfg('fill_tom', 'perc', -11, '16n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 4, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.1}},
         [_dist(0.8, 0.6)],
         [_N]*24 + ['G2', _N, 'E2', _N, 'C2', 'C2', 'A1', 'A1'],
         loop_modulo=8, loop_modulo_remainder=7),
]


class TekTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.TEK
    BPM_RANGE = (162, 172)
    LEVEL_DB = -6.0
    KEY_ROLES = ('kick',)
    SIDECHAIN_DEPTH = 0.8
    SIDECHAIN_RELEASE = 0.35

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        perc = copy.deepcopy(cls._pick(_PERCS))

        _clear_kick_steps(bass, kick)
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        # Every tek bass lives in the gaps between kicks, so the rumble's swell toward the offbeat
        # suits the offbeat and rolling lines alike.
        bass['pattern']['velocities'] = _vel_rumble(bass['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.25, ghost_prob=0.1)

        layers = [kick, bass, hihat, perc]

        second_perc = cls._maybe([p for p in _PERCS if p['id'] != perc['id']], 0.4)
        if second_perc:
            second_perc = copy.deepcopy(second_perc)
            second_perc['pattern']['velocities'] = _vel(second_perc['pattern']['steps'], accent_prob=0.25, ghost_prob=0.1)
            layers.append(second_perc)

        open_hat = cls._maybe(_OPEN_HATS, 0.5)
        if open_hat:
            open_hat = copy.deepcopy(open_hat)
            open_hat['pattern']['velocities'] = _vel(open_hat['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
            layers.append(open_hat)

        # Acid is what sets free-party tekno apart from hard techno, so most tracks get a line.
        acid = cls._maybe(_ACIDS, 0.7)
        if acid:
            acid = copy.deepcopy(acid)
            steps = acid['pattern']['steps']
            acid['pattern']['velocities'] = _vel(steps, accent_prob=0.3, ghost_prob=0.05)
            acid['pattern']['slides'] = _slides(steps, 0.3)
            if random.random() < 0.4:
                acid['entry_loop'] = 2
            layers.append(acid)

        stab = cls._maybe(_STABS, 0.45)
        if stab:
            stab = copy.deepcopy(stab)
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
            layers.append(stab)

        fill = cls._maybe(_FILLS, 0.5)
        if fill:
            layers.append(copy.deepcopy(fill))

        root_pc = cls._apply_key_coherence(layers)
        _tune_kick(kick, root_pc, _KICK_LOWEST_MIDI)
        return layers

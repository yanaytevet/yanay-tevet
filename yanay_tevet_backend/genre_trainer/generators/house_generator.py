import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _dist, _chorus, _filt, _delay,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.6}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.8}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 2.0}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.58, 'sustain': 0.01, 'release': 1.9}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.4}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.5}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.085, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.56, 'sustain': 0.01, 'release': 1.7}},
         [], ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_CLAPS = [
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.8, 0.4)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0, 'release': 0.09}},
         [_reverb(1.0, 0.45)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.005, 'decay': 0.16, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.2, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.004, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.4, 0.52)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0, 'release': 0.12}},
         [_reverb(1.5, 0.45)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    _cfg('clap', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.1, 0.48)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.9, 0.4)],
         [_N,_N,_N,_N,'C2','C2',_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.08, 'release': 0.06}, 'harmonicity': 3.0, 'modulationIndex': 15, 'resonance': 6000, 'octaves': 1.0},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -11, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.2, 'release': 0.15}, 'harmonicity': 2.5, 'modulationIndex': 12, 'resonance': 7000, 'octaves': 0.8},
         [], [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N]),
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.04}, 'harmonicity': 2.0, 'modulationIndex': 10, 'resonance': 8000, 'octaves': 0.8},
         [], [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 440, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012}, 'harmonicity': 4.2, 'modulationIndex': 22, 'resonance': 5500, 'octaves': 1.3},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -12, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.07, 'release': 0.05}, 'harmonicity': 2.2, 'modulationIndex': 11, 'resonance': 7500, 'octaves': 0.9},
         [], ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,_N,_N]),
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.025}, 'harmonicity': 2.8, 'modulationIndex': 13, 'resonance': 6500, 'octaves': 0.85},
         [], [_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,_N]),
]

_BASSES = [
    _cfg('bass', 'bass', -7, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.5, 'release': 0.3}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.3, 'release': 0.3, 'baseFrequency': 300, 'octaves': 2.5}},
         [], ['G1',_N,'G1',_N,'G1','B1',_N,'G1',_N,_N,'G1',_N,'A1',_N,_N,_N,'G1',_N,'G1',_N,'G1','B1',_N,'G1',_N,_N,'D2',_N,'C2',_N,'B1',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.6, 'release': 0.35}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.35, 'sustain': 0.4, 'release': 0.35, 'baseFrequency': 350, 'octaves': 2}},
         [], ['E1',_N,'E1',_N,'E1','G1',_N,'E1',_N,_N,'E1',_N,'D1',_N,_N,'D1','E1',_N,'E1',_N,'G1','E1',_N,'D1',_N,_N,'B1','A1','G1','E1',_N,_N]),
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.8, 'release': 0.3}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.7, 'release': 0.3, 'baseFrequency': 80, 'octaves': 1.5}},
         [], ['A1',_N,_N,_N,'C2',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'E2',_N,_N,_N,'D2',_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.008, 'decay': 0.22, 'sustain': 0.55, 'release': 0.3}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.32, 'sustain': 0.35, 'release': 0.3, 'baseFrequency': 280, 'octaves': 2.2}},
         [], ['C2',_N,'C2',_N,'C2','Eb2',_N,'C2','Bb1',_N,'C2',_N,'G1','Bb1',_N,_N,'C2',_N,'C2','Eb2','F2','Eb2','C2',_N,'Bb1',_N,'G1','Bb1','C2',_N,'Eb2',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.02, 'decay': 0.35, 'sustain': 0.55, 'release': 0.4}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.45, 'release': 0.35, 'baseFrequency': 200, 'octaves': 2.0}},
         [], ['G1',_N,'G1',_N,_N,'G1',_N,'Bb1','G1',_N,'G1',_N,'F1',_N,_N,'G1','G1',_N,'G1','Bb1',_N,'G1',_N,'F1','Eb1',_N,'F1','G1','Bb1',_N,'G1',_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.025, 'decay': 0.38, 'sustain': 0.5, 'release': 0.42}, 'filterEnvelope': {'attack': 0.025, 'decay': 0.42, 'sustain': 0.42, 'release': 0.38, 'baseFrequency': 210, 'octaves': 1.8}},
         [], ['C2',_N,'C2',_N,_N,'C2',_N,'Eb2','C2',_N,'C2',_N,'Bb1',_N,_N,'C2','C2',_N,'C2','Eb2',_N,'C2',_N,'Bb1','Ab1',_N,'Bb1','C2','Eb2',_N,'C2',_N]),
    _cfg('bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.015, 'decay': 0.28, 'sustain': 0.65, 'release': 0.3}, 'filterEnvelope': {'attack': 0.015, 'decay': 0.3, 'sustain': 0.5, 'release': 0.3, 'baseFrequency': 300, 'octaves': 1.8}},
         [], ['A1',_N,_N,_N,'A1',_N,'C2',_N,'A1','G1',_N,_N,'E1',_N,'G1',_N,'A1',_N,_N,_N,'C2','E2',_N,'C2','A1','G1',_N,'E1','G1','A1',_N,_N]),
    _cfg('bass', 'bass', -6, '8n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.008, 'decay': 0.25, 'sustain': 0.6, 'release': 0.35}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.28, 'sustain': 0.45, 'release': 0.3, 'baseFrequency': 250, 'octaves': 2.4}},
         [], ['D2',_N,'D2','F2','A2',_N,'F2','D2','C2',_N,'D2','F2','A2','F2',_N,'D2','D2',_N,'F2','A2','C3',_N,'A2','F2','Eb2',_N,'D2','Eb2','F2',_N,'D2',_N]),
]

_PADS = [
    _cfg('chord_pad', 'pad', -14, '16n', 'AMSynth',
         {'harmonicity': 1.0, 'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.7, 'release': 1.5}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.6, 'release': 1.2}},
         [_reverb(2.5, 0.6), _chorus(0.5, 3, 0.4, 0.3)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,'E2',_N,_N,_N,_N,_N,_N,_N,'F2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('chord_pad', 'pad', -15, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.4, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}},
         [_reverb(3.0, 0.65), _chorus(0.4, 4, 0.5, 0.35)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('chord_pad', 'pad', -16, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.75, 'release': 2.5}, 'modulationEnvelope': {'attack': 0.6, 'decay': 0.3, 'sustain': 0.65, 'release': 2.0}},
         [_reverb(3.5, 0.7)],
         ['G2',_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,_N,_N,_N,_N,_N,'Eb2',_N,_N,_N,_N,_N,_N,_N,'Bb1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('chord_pad', 'pad', -18, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.9, 'release': 3.0}},
         [_reverb(4.0, 0.75)],
         ['D2',_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,'G2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N]),
]


# ---------------------------------------------------------------------------
# FILLS — phrase-level accents gated by loop_modulo.
# loop_modulo=4 fires every 8 bars; loop_modulo=8 fires every 16 bars.
# ---------------------------------------------------------------------------
_FILLS = [
    # White-noise riser into bar 2 of the phrase, every 16 bars
    _cfg('fill_riser', 'perc', -14, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.6, 'decay': 0.05, 'sustain': 0.95, 'release': 0.15}},
         [_reverb(1.5, 0.5), _filt('highpass', 2000, 1.2)],
         ['C3'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=7),
    # Extra clap on the "and" of beat 4 of bar 2, every 8 bars — drives the build
    _cfg('fill_clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.003, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.2, 0.55)],
         [_N]*30 + ['C2', 'C2'],
         loop_modulo=4, loop_modulo_remainder=3),
    # Reverse swell / open hat washes every 16 bars
    _cfg('fill_wash', 'perc', -16, '2n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 1.0, 'decay': 0.4, 'release': 0.8},
          'harmonicity': 3.5, 'modulationIndex': 18, 'resonance': 5000, 'octaves': 1.4},
         [_reverb(2.5, 0.6)],
         [_N]*16 + ['C4'] + [_N]*15,
         loop_modulo=8, loop_modulo_remainder=7),
]


# Optional shaker / hand percussion — adds the classic house "swing"
_PERCS = [
    # 16th shaker — pink noise, very quiet for groove
    _cfg('shaker', 'perc', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 4000, 1)],
         ['C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3',
          'C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3','C3']),
    # Conga-like tone on syncopated 16ths
    _cfg('conga', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 4, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.1}},
         [_reverb(0.4, 0.18)],
         [_N,_N,'C3',_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,
          _N,_N,'C3',_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,'C3',_N]),
    # Rim click pattern
    _cfg('rim', 'perc', -16, '16n', 'MetalSynth',
         {'frequency': 1500, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 3.0, 'modulationIndex': 12, 'resonance': 4000, 'octaves': 1.0},
         [],
         [_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,
          _N,_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N]),
]


# ---------------------------------------------------------------------------
# CHORD STABS — PolySynth voices triggered with comma-separated note strings.
# The player splits on ',' before passing to PolySynth.triggerAttackRelease.
# These are the signature "deep house" chord rhythm on offbeats / syncopation.
# ---------------------------------------------------------------------------
_STABS = [
    # Am7-style stab on the offbeats (deep house feel)
    _cfg('chord_stab', 'stab', -14, '16n', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.0, 'release': 0.18}},
         [_reverb(1.4, 0.4), _filt('lowpass', 2600, 1.5)],
         [_N,_N,'A3,C4,E4',_N,_N,_N,'A3,C4,E4',_N,_N,_N,'G3,B3,D4',_N,_N,_N,'A3,C4,E4',_N,
          _N,_N,'A3,C4,E4',_N,_N,_N,'G3,B3,D4',_N,_N,_N,'F3,A3,C4',_N,_N,_N,'A3,C4,E4',_N]),
    # Em9 syncopated stab
    _cfg('chord_stab', 'stab', -15, '16n', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.008, 'decay': 0.18, 'sustain': 0.05, 'release': 0.22}},
         [_reverb(1.8, 0.45), _filt('lowpass', 2200, 1.4)],
         [_N,'E3,G3,B3,D4',_N,_N,_N,'E3,G3,B3,D4',_N,_N,_N,_N,'C3,E3,G3',_N,_N,'D3,F#3,A3',_N,_N,
          _N,'E3,G3,B3,D4',_N,_N,_N,'E3,G3,B3,D4',_N,_N,_N,_N,'A3,C4,E4',_N,_N,'G3,B3,D4',_N,_N]),
    # Cm-Ab-Fm-G jazzy progression, off-beat stabs
    _cfg('chord_stab', 'stab', -14, '16n', 'PolySynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.0, 'release': 0.15}},
         [_reverb(1.2, 0.42), _filt('lowpass', 2400, 1.6), _chorus(0.6, 3, 0.4, 0.3)],
         [_N,_N,'C4,Eb4,G4',_N,_N,_N,'C4,Eb4,G4',_N,_N,_N,'Ab3,C4,Eb4',_N,_N,_N,'Ab3,C4,Eb4',_N,
          _N,_N,'F3,Ab3,C4',_N,_N,_N,'F3,Ab3,C4',_N,_N,_N,'G3,Bb3,D4',_N,_N,_N,'G3,B3,D4',_N]),
    # Dm7-G7 jazz-house turnaround
    _cfg('chord_stab', 'stab', -15, '16n', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.004, 'decay': 0.14, 'sustain': 0.0, 'release': 0.2}},
         [_reverb(1.6, 0.5), _filt('lowpass', 2300, 1.5), _delay('8n', 0.18, 0.12)],
         [_N,_N,'D3,F3,A3,C4',_N,_N,_N,'D3,F3,A3,C4',_N,_N,_N,_N,_N,'D3,F3,A3,C4',_N,_N,_N,
          _N,_N,'G3,B3,D4,F4',_N,_N,_N,'G3,B3,D4,F4',_N,_N,_N,_N,_N,'G3,B3,D4,F4',_N,_N,_N]),
]


class HouseTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.HOUSE
    BPM_RANGE = (122, 128)
    SWING = 0.12  # Classic house shuffle on 16ths

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        clap = copy.deepcopy(cls._pick(_CLAPS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.22, ghost_prob=0.08)

        layers = [kick, clap, hihat, bass]

        # Chord stab — the harmonic centerpiece of most house tracks. Usually enters after intro.
        if random.random() < 0.7:
            stab = copy.deepcopy(cls._pick(_STABS))
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
            stab['entry_loop'] = random.choice([0, 2, 4])
            layers.append(stab)

        if random.random() < 0.55:
            pad = copy.deepcopy(cls._pick(_PADS))
            layers.append(pad)

        # House gets its swing from layered hand percussion
        if random.random() < 0.5:
            perc = copy.deepcopy(cls._pick(_PERCS))
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.15, ghost_prob=0.2)
            layers.append(perc)

        # Phrase fill (riser / clap / wash) — gated by loop_modulo so it only
        # fires once every 8 or 16 bars.
        if random.random() < 0.6:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        cls._apply_key_coherence(layers)
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _auto, _pingpong, _slides,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

# ---------------------------------------------------------------------------
# KICKS — distorted four-on-the-floor. Acid sits on a driven, slightly grubby
# kick rather than a clean one; the distortion is part of the sound. Every
# entry hits all eight quarters; a few add one 16th pickup before a downbeat.
# ---------------------------------------------------------------------------
_KICKS = [
    # Tight and driven — the default acid floor
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.6, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Harder clip, shorter tail — leaves more room for the 303 between hits
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.5}},
         [_dist(0.8, 0.65)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Pickup 16th into the loop restart
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.7, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Boomier, lower — the 90s warehouse version
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.8}},
         [_dist(0.5, 0.45)],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,
          'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N]),
    # Pickup into bar 2
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.026, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.55}},
         [_dist(0.65, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Short, clicky and heavily saturated
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.01, 'release': 0.45}},
         [_dist(0.85, 0.7)],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,
          'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# CLAPS — optional backbeat on 2 and 4. Kept short so they never compete with
# the 303 squelch for the mid-range.
# ---------------------------------------------------------------------------
_CLAPS = [
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.07}},
         [_reverb(0.6, 0.18)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Pink and gritty
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.08}},
         [_dist(0.4, 0.35), _reverb(0.5, 0.15)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Thin 909-ish snare — highpassed so the low end stays the kick's
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.05}},
         [_filt('highpass', 1200, 0.8), _reverb(0.4, 0.12)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Ghost flam into the last backbeat
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.7, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# CLOSED HATS — running 16ths. The hats are the motor under the 303; they stay
# straight and let velocity (_vel_groove) do the swing.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Straight 16ths
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.006}, 'harmonicity': 8.5, 'modulationIndex': 55, 'resonance': 7000, 'octaves': 2.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Distorted 16ths — rawer, 90s rave texture
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.016, 'release': 0.007}, 'harmonicity': 10, 'modulationIndex': 65, 'resonance': 9000, 'octaves': 2.4},
         [_dist(0.3, 0.3)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 16ths that step out of the kick's way on every quarter
    _cfg('hihat', 'hihat', -9, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.013, 'release': 0.006}, 'harmonicity': 9.0, 'modulationIndex': 58, 'resonance': 7500, 'octaves': 2.1},
         [],
         [_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',
          _N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4']),
    # 16ths with a breath on the last beat — the loop turns around
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.005}, 'harmonicity': 9.5, 'modulationIndex': 60, 'resonance': 8000, 'octaves': 2.2},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',_N,_N,_N,_N]),
    # Very short and bright — a ticking clock
    _cfg('hihat', 'hihat', -11, '16n', 'MetalSynth',
         {'frequency': 1200, 'envelope': {'attack': 0.001, 'decay': 0.008, 'release': 0.004}, 'harmonicity': 11, 'modulationIndex': 70, 'resonance': 10000, 'octaves': 2.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Three of every four 16ths — a little gallop before each beat lands
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 780, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.007}, 'harmonicity': 8.0, 'modulationIndex': 52, 'resonance': 6500, 'octaves': 1.9},
         [],
         ['C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,
          'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N]),
]

# ---------------------------------------------------------------------------
# OPEN HATS — the offbeat "tss" between kicks. With the running 16ths above it
# this is the unmistakable acid/rave hat pattern.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    _cfg('open_hat', 'hihat', -12, '8n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.16, 'release': 0.08}, 'harmonicity': 6.5, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.6},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Noise open hat — closer to a 909
    _cfg('open_hat', 'hihat', -14, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [_filt('highpass', 7000, 0.7)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Long and trashy
    _cfg('open_hat', 'hihat', -13, '8n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.22, 'release': 0.1}, 'harmonicity': 7.5, 'modulationIndex': 48, 'resonance': 7000, 'octaves': 1.8},
         [_dist(0.25, 0.25)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Short open hat, slightly darker
    _cfg('open_hat', 'hihat', -12, '8n', 'MetalSynth',
         {'frequency': 520, 'envelope': {'attack': 0.001, 'decay': 0.1, 'release': 0.05}, 'harmonicity': 5.8, 'modulationIndex': 36, 'resonance': 5000, 'octaves': 1.5},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# 303 LINES — the genre. A MonoSynth with a high-Q filter and a fast, deep
# filter envelope gives the per-note "zap"; amp sustain holds the note long
# enough for slides (set per track by _slides) to glide audibly; accents come
# from velocity. Effect 0 is the cutoff knob, swept across the loop by
# automation, and the distortion after it is what makes it scream. Lines are
# 16th-note phrases with octave jumps, chromatic neighbours and rests, and
# they run straight across the kick, as a real 303 pattern does.
# ---------------------------------------------------------------------------
_ACID_BASSES = [
    # A — octave bounce, the textbook acid figure
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.35, 'release': 0.04},
          'filter': {'type': 'lowpass', 'Q': 11, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.13, 'sustain': 0.05, 'release': 0.05, 'baseFrequency': 170, 'octaves': 4.0}},
         [_filt('lowpass', 900, 3), _dist(0.6, 0.5)],
         ['A1','A1','A2','A1',_N,'A1','C2','A2','A1',_N,'A1','G2','A1','A2',_N,'E2',
          'A1','A1','A2','A1',_N,'A1','C2','A2','A1',_N,'Eb2','D2','C2',_N,'A2','G1'],
         automation=[_auto('effect:0:frequency', 300, 3800, 'tri')]),
    # E Phrygian — the flat second gives the menace
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0.3, 'release': 0.04},
          'filter': {'type': 'lowpass', 'Q': 13, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.04, 'release': 0.04, 'baseFrequency': 150, 'octaves': 4.6}},
         [_filt('lowpass', 800, 3.5), _dist(0.65, 0.55)],
         ['E1',_N,'E2','E1','F1','E1',_N,'E2',_N,'E1','G1','E1','Bb1',_N,'E2','E1',
          'E1',_N,'E2','E1','F1','E1',_N,'E2',_N,'G1','E2',_N,'F2','E2','D2','B1'],
         automation=[_auto('effect:0:frequency', 280, 4200, 'tri')]),
    # D — rolling single note, the movement is all octave and filter
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.22, 'sustain': 0.4, 'release': 0.05},
          'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0.06, 'release': 0.05, 'baseFrequency': 200, 'octaves': 3.6}},
         [_filt('lowpass', 1000, 3), _dist(0.55, 0.5)],
         ['D2','D2','D3','D2','D2','D3','D2',_N,'D2','D2','D3','D2','F2','D3',_N,'D2',
          'D2','D2','D3','D2','D2','D3','D2',_N,'C2','C2','C3','C2','Eb2',_N,'C3','D2'],
         automation=[_auto('effect:0:frequency', 350, 3400, 'ramp')]),
    # G — question and answer with rests; the gaps make the slides pop
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.25, 'sustain': 0.45, 'release': 0.05},
          'filter': {'type': 'lowpass', 'Q': 9, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0.08, 'release': 0.06, 'baseFrequency': 140, 'octaves': 4.2}},
         [_filt('lowpass', 700, 3), _dist(0.5, 0.45), _delay('8n.', 0.25, 0.14)],
         ['G1',_N,_N,'G2',_N,'G1','Bb1',_N,'G1',_N,'G2',_N,'C2','Bb1','G1',_N,
          'G1',_N,_N,'G2',_N,'G1','F2',_N,'G1','G2',_N,'D2',_N,'F1','G1','G2'],
         automation=[_auto('effect:0:frequency', 260, 3600, 'tri')]),
    # A — hypnotic chromatic rub, "Higher State" territory
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.25, 'release': 0.03},
          'filter': {'type': 'lowpass', 'Q': 15, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.03, 'release': 0.03, 'baseFrequency': 130, 'octaves': 5.0}},
         [_filt('lowpass', 850, 4), _dist(0.75, 0.6)],
         ['A1','A2','A1','A1','Bb1','A1','A2',_N,'A1','A1','C2','A1','A2',_N,'Bb1','A1',
          'A1','A2','A1','A1','Bb1','A1','A2',_N,'E2','Eb2','D2','C2','A1',_N,'A2','A1'],
         automation=[_auto('effect:0:frequency', 250, 4500, 'tri')]),
    # C minor — low/high call across two octaves
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.3, 'release': 0.04},
          'filter': {'type': 'lowpass', 'Q': 12, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.05, 'release': 0.04, 'baseFrequency': 180, 'octaves': 3.8}},
         [_filt('lowpass', 900, 3), _dist(0.6, 0.55)],
         ['C2',_N,'C3',_N,'C2','Eb2',_N,'C3','C2',_N,'G2','C2','Bb1',_N,'C3',_N,
          'C2',_N,'C3',_N,'C2','Eb2',_N,'C3','F2',_N,'Eb2','C2','G2',_N,'Bb2','C3'],
         automation=[_auto('effect:0:frequency', 300, 3900, 'tri')]),
    # F minor — nonstop squelch, almost no rests
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.22, 'release': 0.03},
          'filter': {'type': 'lowpass', 'Q': 14, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.07, 'sustain': 0.02, 'release': 0.03, 'baseFrequency': 160, 'octaves': 4.8}},
         [_filt('lowpass', 750, 4), _dist(0.7, 0.6)],
         ['F1','F1','F2','F1','Ab1','F1','F1','F2','F1','C2','F1','F2','Eb2','F1','F2','F1',
          'F1','F1','F2','F1','Ab1','F1','F1','F2','Db2','C2','Ab1','F1','F2',_N,'F1','Eb2'],
         automation=[_auto('effect:0:frequency', 220, 4000, 'ramp')]),
]

# ---------------------------------------------------------------------------
# SECOND 303 — a higher, sparser acid line answering the bass, the classic
# two-303 stack. Same squelch recipe, a delay to push it back, and more rests
# so the two lines interlock instead of piling up.
# ---------------------------------------------------------------------------
_ACID_LEADS = [
    # A — answers on the offbeats
    _cfg('acid_lead', 'lead', -12, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.22, 'sustain': 0.35, 'release': 0.05},
          'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.05, 'release': 0.05, 'baseFrequency': 260, 'octaves': 3.6}},
         [_filt('lowpass', 1200, 3), _dist(0.5, 0.45), _delay('8n.', 0.32, 0.22)],
         ['A2',_N,'A3',_N,_N,'A2',_N,'C3','A3',_N,_N,'A2',_N,'G3','A3',_N,
          'A2',_N,'A3',_N,_N,'A2',_N,'E3','Eb3','D3',_N,'A2',_N,_N,'A3',_N],
         automation=[_auto('effect:0:frequency', 450, 4800, 'tri')]),
    # E Phrygian — tight stutter around the root
    _cfg('acid_lead', 'lead', -13, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0.3, 'release': 0.04},
          'filter': {'type': 'lowpass', 'Q': 12, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.04, 'release': 0.04, 'baseFrequency': 240, 'octaves': 4.2}},
         [_filt('lowpass', 1100, 3.5), _dist(0.55, 0.5), _pingpong('8n', 0.3, 0.2)],
         ['E3','E3',_N,'F3','E3',_N,_N,'E4',_N,'E3','G3',_N,'E3',_N,'D3',_N,
          'E3','E3',_N,'F3','E3',_N,_N,'B3','C4',_N,'B3',_N,'G3',_N,'F3','E3'],
         automation=[_auto('effect:0:frequency', 400, 4400, 'tri')]),
    # D — long gaps, octave pokes
    _cfg('acid_lead', 'lead', -12, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.25, 'sustain': 0.45, 'release': 0.06},
          'filter': {'type': 'lowpass', 'Q': 9, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0.06, 'release': 0.05, 'baseFrequency': 280, 'octaves': 3.4}},
         [_filt('lowpass', 1300, 3), _dist(0.45, 0.4), _delay('8n.', 0.38, 0.25)],
         ['D3',_N,_N,'D3','D4',_N,'D3',_N,_N,_N,'F3','D3',_N,'C3',_N,_N,
          'D3',_N,_N,'D3','D4',_N,'D3',_N,'A3','G3','F3',_N,'D3',_N,_N,_N],
         automation=[_auto('effect:0:frequency', 500, 4200, 'ramp')]),
    # G — stuttering triple then a run home
    _cfg('acid_lead', 'lead', -13, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0.28, 'release': 0.04},
          'filter': {'type': 'lowpass', 'Q': 13, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.09, 'sustain': 0.03, 'release': 0.04, 'baseFrequency': 220, 'octaves': 4.5}},
         [_filt('lowpass', 1000, 3.5), _dist(0.6, 0.5), _delay('8n', 0.25, 0.16)],
         ['G2','G2','G3',_N,'G2',_N,_N,'G2','Bb2','G2',_N,'G3',_N,_N,'G2',_N,
          'G2','G2','G3',_N,'G2',_N,_N,'D3','C3',_N,'Bb2','G2',_N,'F3','G3',_N],
         automation=[_auto('effect:0:frequency', 380, 4600, 'tri')]),
    # C minor — held notes slide into each other
    _cfg('acid_lead', 'lead', -12, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.3, 'sustain': 0.5, 'release': 0.06},
          'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0.08, 'release': 0.06, 'baseFrequency': 250, 'octaves': 3.8}},
         [_filt('lowpass', 1150, 3), _dist(0.5, 0.45), _pingpong('8n.', 0.35, 0.22)],
         ['C3',_N,'C3','C4',_N,_N,'C3',_N,'Eb3',_N,'C3',_N,'G3',_N,_N,'C3',
          'C3',_N,'C3','C4',_N,_N,'Bb2',_N,'C3',_N,'Eb3','F3',_N,'Eb3','C3',_N],
         automation=[_auto('effect:0:frequency', 420, 4300, 'tri')]),
]


class AcidTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.ACID_TECHNO
    BPM_RANGE = (132, 140)
    LEVEL_DB = -7.0
    KEY_ROLES = ('bass',)
    # The 303 crosses the kick, so it only dips a little and comes straight back.
    SIDECHAIN_DEPTH = 0.7
    SIDECHAIN_RELEASE = 0.4

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_ACID_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        # Heavy accents are half the 303 character: the accented notes jump out of the line.
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.4, ghost_prob=0.05)
        bass['pattern']['slides'] = _slides(bass['pattern']['steps'], random.uniform(0.2, 0.35))

        layers = [kick, hihat, bass]

        if random.random() < 0.85:
            open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))
            open_hat['pattern']['velocities'] = _vel(open_hat['pattern']['steps'], accent_prob=0.25, ghost_prob=0.0)
            layers.append(open_hat)

        if random.random() < 0.6:
            clap = copy.deepcopy(cls._pick(_CLAPS))
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        if random.random() < 0.5:
            lead = copy.deepcopy(cls._pick(_ACID_LEADS))
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.35, ghost_prob=0.05)
            lead['pattern']['slides'] = _slides(lead['pattern']['steps'], random.uniform(0.2, 0.35))
            # The second line arrives after the main 303 has been heard on its own.
            lead['entry_loop'] = random.choice([0, 2, 2, 4])
            layers.append(lead)

        if random.random() < 0.3:
            hihat['dropout_prob'] = random.choice([0.15, 0.2, 0.25])

        cls._apply_key_coherence(layers)
        return layers

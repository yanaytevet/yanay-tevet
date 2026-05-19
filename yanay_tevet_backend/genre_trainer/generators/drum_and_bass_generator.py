import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _filt, _chorus,
    _vel, _vel_groove, _vel_kick, _vel_snare, _delay,
)

# ---------------------------------------------------------------------------
# KICKS — DnB two-step and syncopated variants.
# MembraneSynth with short pitch decay for that punchy sub impact.
# Velocities applied dynamically in _generate_layers via _vel_kick.
# ---------------------------------------------------------------------------
_KICKS = [
    # Two-step classic: 1 + 2.75 per bar — the defining DnB groove
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.2}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N]),
    # Syncopated: beat 1 + pickup 16th before beat 3 + early beat 3
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 1.1}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N]),
    # Staggered: anticipation kick on beat 2.5 each bar
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,'C1',_N,_N,_N,_N,'C1',_N,'C1',_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N]),
    # Sparse half-time feel with double-kick pickup into bar 2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.1}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N]),
    # Two-step with variation: bar 2 has an extra syncopated hit
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,'C1']),
    # Jump-up: 1, 2.75, 3 in bar 1; 1, 2.75, 3.5 in bar 2
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,'C1','C1',_N,_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N]),
    # Dense fill in bar 2: open bar 1, rolling pickup into bar 2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,'C1',_N,_N,_N,_N,_N]),
    # Bar-split: sparse bar 1, dense pickup bar 2 into beat 1
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.31, 'sustain': 0.01, 'release': 1.05}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,'C1',
          'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,'C1',_N,_N,_N,_N,_N]),
    # Double-kick on beat 3.75 for rolling energy
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.1}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1','C1',_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1','C1',_N,_N]),
    # Fluid: kicks on 1, 1.75, 3 — floaty two-step variant
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.041, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0.01, 'release': 1.15}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,'C1','C1',_N,_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# SNARES — backbeat foundation with ghost hits for organic feel.
# Main hits at beats 2 & 4 (steps 4,12,20,28); ghost hits at other positions.
# _vel_snare applied in _generate_layers: main → 0.78–0.95, ghost → 0.16–0.32.
# ---------------------------------------------------------------------------
_SNARES = [
    # Backbeat + ghost before beat 3 and before bar-2 beat 3
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.6, 0.25)],
         [_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,
          _N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N]),
    # Off-beat ghosts on the "and" of beats 2 and 4
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.07}},
         [_reverb(0.8, 0.3)],
         [_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N,
          _N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
    # Fill into bar 2: ghost roll on steps 14–15 then double-hit landing
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.7, 0.28)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2','C2',
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N]),
    # Clean backbeat — ghost only on "e" of beat 4 each bar
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.5, 0.22)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2',
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2']),
    # Heavy room snare with pre-beat ghost and stutter on beat 4
    _cfg('snare', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.14, 'sustain': 0, 'release': 0.06}},
         [_reverb(1.0, 0.3)],
         [_N,_N,_N,'C4','C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,'C4',
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,'C4',_N]),
    # Rim/ghost layer: dense irregular pattern for texture behind main snare
    _cfg('snare', 'snare', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',
          _N,_N,'C4',_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,_N,'C4',_N]),
    # Syncopated snare: shifted beat 2 + ghost setup into beats
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.7, 0.28)],
         [_N,_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,'C2',_N,
          _N,_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,'C2',_N]),
    # Ghost-heavy: fills on the "ah" of every beat
    _cfg('snare', 'snare', -6, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.9, 0.28)],
         [_N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,'C2',
          _N,_N,_N,_N,'C2',_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,'C2']),
    # DnB feel: ghost on "e" of beat 2 and "and" of beat 3 each bar
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.65, 0.26)],
         [_N,_N,_N,_N,'C2','C2',_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2','C2',_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — metallic 16th patterns, velocity applied via _vel_groove in
# _generate_layers so quarter-note accents and off-beat ghosts emerge naturally.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Full 16ths — dense driving grid
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008},
          'harmonicity': 7.0, 'modulationIndex': 45, 'resonance': 6000, 'octaves': 1.8},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Off-beats only — Amen-break hi-hat spacing
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 5500, 'octaves': 1.7},
         [],
         [_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',
          _N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4']),
    # Full 16ths, brighter tone
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.007},
          'harmonicity': 7.5, 'modulationIndex': 48, 'resonance': 6500, 'octaves': 1.9},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Syncopated groups: 2+1 feel with breathing gaps
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 580, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.009},
          'harmonicity': 6.8, 'modulationIndex': 44, 'resonance': 5800, 'octaves': 1.8},
         [],
         ['C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',_N,
          'C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',_N]),
    # 8th notes with 16th fills into beat 4 — creates DnB push
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 620, 'envelope': {'attack': 0.001, 'decay': 0.013, 'release': 0.008},
          'harmonicity': 7.2, 'modulationIndex': 46, 'resonance': 6200, 'octaves': 1.85},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4','C4','C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4','C4','C4',_N]),
    # Sparse breathing: dotted-8th feel with gaps letting kick/snare dominate
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 570, 'envelope': {'attack': 0.001, 'decay': 0.016, 'release': 0.01},
          'harmonicity': 6.3, 'modulationIndex': 41, 'resonance': 5600, 'octaves': 1.75},
         [],
         ['C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N]),
    # Triplet-feel: groups of 3 give shuffle energy in a 16th grid
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 590, 'envelope': {'attack': 0.001, 'decay': 0.011, 'release': 0.007},
          'harmonicity': 7.1, 'modulationIndex': 47, 'resonance': 6100, 'octaves': 1.82},
         [],
         ['C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,
          'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N]),
]

# ---------------------------------------------------------------------------
# BASSES — Reese/AM/FM basses with call-and-response phrasing.
# Vary between busier rolling patterns and half-time breathing patterns.
# Velocities applied in _generate_layers.
# ---------------------------------------------------------------------------
_BASSES = [
    # A minor — rolling 16ths with stepwise approach and octave jump
    _cfg('reese_bass', 'bass', -5, '8n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.7, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.1, 'decay': 0.2, 'sustain': 0.8, 'release': 0.2}},
         [_dist(0.3, 0.4), _filt('lowpass', 900, 3)],
         ['A1',_N,'A1',_N,'G1','A1',_N,_N,'E1','A1',_N,'G1','A1',_N,_N,_N,
          'A1',_N,'C2','A1','G1',_N,'A1',_N,'E1',_N,'D1','E1','G1','A1',_N,_N]),
    # D minor — quarter-note walking with call-and-response across bars
    _cfg('reese_bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.6, 'release': 0.3},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.4, 'release': 0.3, 'baseFrequency': 200, 'octaves': 2}},
         [],
         ['D1',_N,_N,_N,'F1',_N,_N,_N,'D1',_N,_N,_N,'A1',_N,_N,_N,
          'D1',_N,_N,_N,'G1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N]),
    # F minor — ascending motif with chromatic neighbour tones
    _cfg('reese_bass', 'bass', -5, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.18, 'sustain': 0.55, 'release': 0.28},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.28, 'sustain': 0.35, 'release': 0.28, 'baseFrequency': 180, 'octaves': 2.2}},
         [_chorus(2, 2, 0.4, 0.2)],
         ['F1',_N,'F1','G1','A1',_N,'G1',_N,'F1',_N,'E1',_N,'D1','E1','F1',_N,
          'F1',_N,'G1',_N,'A1',_N,'C2','A1','G1',_N,'F1',_N,'E1','D1','E1',_N]),
    # G major — dense 16th rolling with varied note density between bars
    _cfg('reese_bass', 'bass', -4, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_dist(0.38, 0.45), _filt('lowpass', 1000, 3.5)],
         ['G1',_N,'G1','A1','G1','F1','G1',_N,'E1','G1',_N,'F1','E1',_N,'D1','E1',
          'G1',_N,'G1','A1','C2','A1','G1','F1','E1','D1','C1',_N,'D1','E1','G1',_N]),
    # D minor — punchy one-note motif with rhythmic displacement
    _cfg('reese_bass', 'bass', -4, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_chorus(1.5, 3.5, 0.7, 0.5), _dist(0.3, 0.3)],
         ['D1',_N,'D1','D1',_N,'D1',_N,'D1','C1',_N,'D1',_N,'C1','D1',_N,_N,
          'D1',_N,'D1','F1','D1',_N,_N,'D1','C1','D1',_N,'C1','Bb0',_N,'C1','D1']),
    # G minor — similar motif transposed, creates alternation when picked
    _cfg('reese_bass', 'bass', -5, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.65, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_chorus(1.2, 3.5, 0.65, 0.48), _dist(0.28, 0.28)],
         ['G1',_N,'G1','G1',_N,'G1',_N,'G1','F1',_N,'G1',_N,'F1','G1',_N,_N,
          'G1',_N,'G1','Bb1','G1',_N,_N,'G1','F1','G1',_N,'F1','Eb1',_N,'F1','G1']),
    # A minor — AM bass with wider note range, high-to-low arc across 2 bars
    _cfg('reese_bass', 'bass', -3, '8n', 'AMSynth',
         {'harmonicity': 0.75, 'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.72, 'release': 0.32},
          'modulationEnvelope': {'attack': 0.12, 'decay': 0.18, 'sustain': 0.82, 'release': 0.22}},
         [_dist(0.35, 0.42), _filt('lowpass', 1100, 2.5)],
         ['A1',_N,_N,'C2',_N,'A1',_N,'G1','A1',_N,'E1',_N,'G1','A1',_N,_N,
          'A1',_N,_N,'C2','E2',_N,'D2','C2','A1',_N,'G1',_N,'A1','C2',_N,_N]),
    # A minor — half-time: bar 1 open, bar 2 answering phrase
    _cfg('reese_bass', 'bass', -4, '8n', 'AMSynth',
         {'harmonicity': 0.6, 'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.65, 'release': 0.35},
          'modulationEnvelope': {'attack': 0.08, 'decay': 0.22, 'sustain': 0.75, 'release': 0.25}},
         [_dist(0.32, 0.38), _filt('lowpass', 950, 3)],
         ['A1',_N,_N,_N,'E1',_N,'A1',_N,'G1',_N,_N,_N,'E1',_N,_N,_N,
          'A1',_N,'A2',_N,'G1',_N,'E1',_N,'D1',_N,'E1','G1','A1',_N,_N,_N]),
    # E minor — sparse with stepwise motion and deliberate rhythmic gaps
    _cfg('reese_bass', 'bass', -3, '8n', 'FMSynth',
         {'harmonicity': 0.45, 'modulationIndex': 10, 'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.6, 'release': 0.32},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.12, 'sustain': 0.35, 'release': 0.28}},
         [_dist(0.4, 0.44), _filt('lowpass', 1050, 3.2)],
         ['E1',_N,_N,_N,'B0',_N,'E1',_N,'D1',_N,_N,_N,'B0',_N,'C1','D1',
          'E1',_N,_N,'G1','E1',_N,'D1',_N,'C1',_N,'B0',_N,'G0',_N,'B0',_N]),
    # G minor — rolling 16ths with varied density: busy bar 1, melodic bar 2
    _cfg('reese_bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.16, 'sustain': 0.5, 'release': 0.25},
          'filterEnvelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.3, 'release': 0.25, 'baseFrequency': 190, 'octaves': 2.3}},
         [_chorus(1.8, 2.5, 0.45, 0.22)],
         ['G1','G1','A1','G1','F1','G1','A1',_N,'G1','G1','F1','G1','E1',_N,'F1','G1',
          'G1',_N,'A1','G1','F1','G1',_N,'E1','D1','E1','F1',_N,'G1','A1',_N,_N]),
]

# ---------------------------------------------------------------------------
# ATMOSPHERES — pads, sub drones, airy textures for breakdown moments.
# Used probabilistically in _generate_layers.
# ---------------------------------------------------------------------------
_ATMOSPHERES = [
    # D minor pad — slow harmonic movement every half-bar
    _cfg('atmosphere', 'pad', -20, '16n', 'AMSynth',
         {'harmonicity': 0.25, 'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.7, 'release': 2.0},
          'modulationEnvelope': {'attack': 0.6, 'decay': 0.3, 'sustain': 0.6, 'release': 2.0}},
         [_reverb(4.0, 0.75)],
         ['D2',_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,
          'D2',_N,_N,_N,_N,_N,_N,_N,'G2',_N,_N,_N,_N,_N,_N,_N]),
    # A minor sine — very long decay, sub presence
    _cfg('atmosphere', 'pad', -22, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5}},
         [_reverb(5.0, 0.8)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # G minor FM pad — slow FM modulation creates shimmer
    _cfg('atmosphere', 'pad', -21, '16n', 'FMSynth',
         {'harmonicity': 0.1, 'modulationIndex': 5, 'envelope': {'attack': 0.4, 'decay': 0.4, 'sustain': 0.75, 'release': 2.2},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.65, 'release': 2.0}},
         [_reverb(4.5, 0.78), _dist(0.2, 0.15)],
         ['G1',_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,_N,_N,_N,_N,_N,
          'G1',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N]),
    # Sub drone — ultra-low FMSynth fills sub frequencies in breakdowns
    _cfg('sub_drone', 'pad', -22, '4n', 'FMSynth',
         {'harmonicity': 0.1, 'modulationIndex': 50,
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.7, 'release': 2.5},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.5, 'release': 2.0}},
         [_reverb(4.5, 0.7), _filt('lowpass', 300, 1)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'E1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Airy triangle pad — high register shimmer, very wet reverb
    _cfg('airy_pad', 'pad', -26, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.7, 'release': 3.0}},
         [_reverb(6.0, 0.9), _chorus(0.5, 4.0, 0.6, 0.5)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,
          'G3',_N,_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,_N,_N]),
]


class DrumAndBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.DRUM_AND_BASS
    BPM_RANGE = (170, 176)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.22, ghost_prob=0.08)

        layers = [kick, snare, bass]

        # Hi-hat — always present; occasionally layer a second sparse hat for texture
        hihat_idx = random.randrange(len(_HIHATS))
        hihat = copy.deepcopy(_HIHATS[hihat_idx])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        layers.append(hihat)

        if random.random() < 0.38:
            other_hats = [h for i, h in enumerate(_HIHATS) if i != hihat_idx]
            hihat2 = copy.deepcopy(random.choice(other_hats))
            hihat2['pattern']['velocities'] = _vel_groove(hihat2['pattern']['steps'])
            hihat2['volume'] = hihat2['volume'] - 4
            layers.append(hihat2)

        # Atmosphere — present in more than half of tracks
        atm = cls._maybe(_ATMOSPHERES, 0.55)
        if atm:
            layers.append(copy.deepcopy(atm))

        return layers

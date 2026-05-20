import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _auto,
    _vel, _vel_groove, _vel_kick,
)

# ---------------------------------------------------------------------------
# KICKS — 4/4 foundation with forest-psy syncopation variants.
# All use long-decay MembraneSynth for that deep psytrance sub tail.
# ---------------------------------------------------------------------------
_KICKS = [
    # Standard 4/4 — clean sub, light drive
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.2, 0.3)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Standard 4/4 — heavier distortion
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.3, 0.4)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Standard 4/4 — maximum crunch
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.85, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # "Da-dum" — anticipation hit just before beat 1 of bar 2 (step 15) and loop end (step 31)
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.55, 0.45)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Rolling double — extra hit two 16ths before beat 3 in each bar (steps 6, 22)
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.25, 0.35)],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # 3-per-bar — beat 1, beat 3, beat 4 (forest psy triplet feel)
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.036, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.33, 'sustain': 0.01, 'release': 1.25}},
         [_dist(0.4, 0.4)],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Psychedelic rolling — hits at 0,5,10,16,21,26 (5+5+6 cycle gives floating feel)
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.3, 0.35)],
         ['C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N]),
    # Split bar — beat1+3 only in bar1, then dense fill in bar2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.7, 0.45)],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — dark low-frequency metallic / noise hats, groove-focused.
# _vel_groove applied at generation time for accent variation.
# ---------------------------------------------------------------------------
_HIHATS = [
    # 8th-note pattern, low metallic — classic dark psy spacing
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.5},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # 8th-on-downbeat — hits every other 16th starting on the 1
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.5},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # Noise hat — distorted hiss, off-beat
    _cfg('hihat', 'hihat', -15, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01}},
         [_dist(0.6, 0.55)],
         [_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',
          _N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4']),
    # Straight 16ths — dense, tribal
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Sparse syncopated — breathing gaps create forest feel
    _cfg('hihat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008}},
         [_dist(0.7, 0.6)],
         [_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N,
          _N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N]),
    # Irregular metallic — alien triplet-feel groupings
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 350, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01},
          'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 5000, 'octaves': 1.4},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,_N]),
    # Groove-forward — accent on beat and off-beat creates swing
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 310, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 6.2, 'modulationIndex': 38, 'resonance': 5300, 'octaves': 1.5},
         [],
         ['C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,
          'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N]),
    # Dark open hat texture — longer decay for open-hat feel
    _cfg('hihat', 'hihat', -19, '16n', 'MetalSynth',
         {'frequency': 260, 'envelope': {'attack': 0.001, 'decay': 0.045, 'release': 0.02},
          'harmonicity': 5.0, 'modulationIndex': 32, 'resonance': 4500, 'octaves': 1.3},
         [_reverb(1.2, 0.2)],
         [_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# GHOST PERCUSSION — pure rhythmic role: clicks, metallic hits, deep toms.
# Short decays only. No sustained reverb that would bleed into the atmospheric
# space reserved for _MOD_LAYERS and _AMBIENT_LAYERS.
# ---------------------------------------------------------------------------
_GHOST_PERCS = [
    # High-frequency click layer — transient noise through HPF
    _cfg('click', 'perc', -20, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.006, 'sustain': 0, 'release': 0.004}},
         [_filt('highpass', 7000, 3)],
         [_N,_N,'C4',_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N]),
    # Mid-register metallic hit — dark bell-like, sparse
    _cfg('metal_hit', 'perc', -22, '16n', 'MetalSynth',
         {'frequency': 180, 'envelope': {'attack': 0.001, 'decay': 0.2, 'release': 0.08},
          'harmonicity': 3.1, 'modulationIndex': 18, 'resonance': 2600, 'octaves': 0.8},
         [_dist(0.25, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N]),
    # Deep tom — low membrane, sparse tribal accent
    _cfg('deep_tom', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 9,
          'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.15}},
         [_dist(0.4, 0.35)],
         [_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# BASSES — FMSynth and MonoSynth with movement: rolling triplets, octave jumps,
# chromatic tension, call/response phrasing. Phrygian/Locrian flavour throughout.
# Punchy envelopes (reduced sustain) for modern darkpsy feel.
# ---------------------------------------------------------------------------
_FM_GROWL = {
    'harmonicity': 0.5, 'modulationIndex': 45,
    'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.2, 'release': 0.15},
    'modulationEnvelope': {'attack': 0.003, 'decay': 0.06, 'sustain': 0.12, 'release': 0.1},
}
_FM_SUB = {
    'harmonicity': 0.15, 'modulationIndex': 50,
    'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.15, 'release': 0.18},
    'modulationEnvelope': {'attack': 0.003, 'decay': 0.05, 'sustain': 0.08, 'release': 0.12},
}
_FM_MID = {
    'harmonicity': 2.0, 'modulationIndex': 28,
    'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.25, 'release': 0.12},
    'modulationEnvelope': {'attack': 0.003, 'decay': 0.06, 'sustain': 0.15, 'release': 0.1},
}
_MONO_SAW = {
    'oscillator': {'type': 'sawtooth'},
    'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.18, 'release': 0.12},
    'filterEnvelope': {'attack': 0.003, 'decay': 0.08, 'sustain': 0.08, 'release': 0.1,
                       'baseFrequency': 110, 'octaves': 5.5},
}

_BASSES = [
    # Rolling staccato with call/response — A Phrygian, chromatic neighbours, octave jump at bar2
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.7, 0.5), _filt('lowpass', 550, 5)],
         ['A0','A0','Bb0','A0',_N,_N,'A0',_N,'C1','A0',_N,'A0',_N,_N,'Ab0',_N,
          'A0','A0','Bb0','A0',_N,'A0',_N,_N,'A1',_N,'A0',_N,_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 180, 2800, 'tri')]),
    # Octave-jumping E Phrygian — aggressive register leaps
    _cfg('dark_bass', 'bass', -4, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.65, 0.5), _filt('lowpass', 500, 6)],
         ['E0',_N,'E1',_N,'E0','E1',_N,'E0','F0',_N,'F1',_N,'E0',_N,_N,'E1',
          'E0',_N,'E1',_N,'F0',_N,'F1','E0','Bb0',_N,_N,'E0',_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 160, 2400, 'tri')]),
    # Chromatic descent — E1 down to A0 then Phrygian pulse
    _cfg('dark_bass', 'bass', -3, '16n', 'MonoSynth', _MONO_SAW,
         [_dist(0.8, 0.55), _filt('lowpass', 650, 8)],
         ['E1',_N,'Eb1',_N,'D1',_N,'Db1',_N,'C1',_N,'B0',_N,'Bb0',_N,'A0',_N,
          'A0',_N,'A0','Bb0','A0',_N,'Ab0',_N,'A0','Bb0',_N,'A0',_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 200, 3000, 'tri')]),
    # Triplet-feel rolling — groups of 3 in 16th grid, D Phrygian
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.75, 0.55), _filt('lowpass', 500, 5)],
         ['D1','D1','D1',_N,'D1','D1','D1',_N,'Eb1','Eb1','Eb1',_N,'D1','D1','D1',_N,
          'Db1','Db1','Db1',_N,'D1','D1',_N,'D1',_N,_N,'D1','D1','D1',_N,_N,_N]),
    # Staccato pulse — aggressive C with chromatic slides
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth', _FM_MID,
         [_dist(0.9, 0.6), _filt('bandpass', 480, 5, 0.8)],
         ['C1','C1',_N,'C1',_N,'C1','Db1',_N,'C1',_N,'C1',_N,'Bb0',_N,'C1','C1',
          'C1',_N,'C1','Eb1',_N,'C1',_N,'C1','Db1','C1',_N,_N,'C1',_N,'Bb0',_N]),
    # Sub pressure — Bb0 rolling with tritone (E0) call/response
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth', _FM_SUB,
         [_dist(0.85, 0.6), _reverb(0.5, 0.1)],
         ['Bb0','Bb0',_N,'Bb0',_N,'Bb0','B0',_N,'Bb0',_N,'Bb0',_N,'Ab0',_N,'Bb0','Bb0',
          'Bb0',_N,'Bb0','Db1',_N,'Bb0',_N,'Bb0','B0','Bb0',_N,_N,'Ab0',_N,'G0',_N]),
    # Deep sub G — MonoSynth squelch, filter automation creates movement
    _cfg('dark_bass', 'bass', -3, '16n', 'MonoSynth', _MONO_SAW,
         [_dist(0.85, 0.6), _filt('lowpass', 400, 9)],
         ['G0',_N,'G0','Ab0','G0',_N,'F0','G0','G0',_N,'G0',_N,'Ab0','G0',_N,'F0',
          'G0',_N,'G0','Bb0','G0','Ab0',_N,'G0','F0',_N,'Eb0','F0','G0',_N,_N,_N],
         automation=[_auto('effect:1:frequency', 120, 2500, 'tri')]),
    # Hypnotic B0 motif — one note with rhythmic variation, tritone accent
    _cfg('dark_bass', 'bass', -4, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.7, 0.5), _filt('lowpass', 520, 6)],
         ['B0',_N,'B0','B0',_N,'B0',_N,_N,'B0','B0',_N,'B0',_N,'B0','B0',_N,
          'B0',_N,'B0',_N,'B0','B0',_N,'B0',_N,_N,'F0',_N,'B0',_N,_N,_N]),
    # Growly FM A minor — original pattern style but punchier envelope
    _cfg('dark_bass', 'bass', -3, '16n', 'FMSynth',
         {'harmonicity': 0.25, 'modulationIndex': 30,
          'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.3, 'release': 0.15},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.05, 'sustain': 0.12, 'release': 0.1}},
         [_dist(0.7, 0.5), _filt('lowpass', 600, 4)],
         ['A1',_N,'A1','Bb1','A1',_N,'G1','A1','F1','A1',_N,'G1','Eb1',_N,'F1','G1',
          'A1',_N,'A1','Bb1','C2','Bb1','A1','G1','F1',_N,'Eb1',_N,'F1','G1',_N,_N]),
]

# ---------------------------------------------------------------------------
# PSY MOTIFS — the harmonic core; exactly one per track.
# Each defines a clear tonal/textural identity. Patterns are sparse: events
# land with intent, separated by silence. No dual rhythmic+atmospheric role.
# ---------------------------------------------------------------------------
_PSY_MOTIFS = [
    # FM shriek — high harmonic hits at tritone/b2 intervals, pure harmonic accent
    _cfg('shriek', 'lead', -22, '16n', 'FMSynth',
         {'harmonicity': 12, 'modulationIndex': 28,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.0, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.08}},
         [_dist(0.7, 0.6), _reverb(1.4, 0.35, 0.01)],
         [_N,_N,'Eb5',_N,_N,_N,_N,_N,'A4',_N,_N,_N,_N,'Bb4',_N,_N,
          _N,_N,_N,_N,'Eb5',_N,_N,_N,'A4',_N,_N,_N,_N,_N,'Bb4',_N]),
    # Eerie AMSynth stab — 4 events in 2 bars with long reverb tail, pure harmonic
    _cfg('stab', 'lead', -19, '16n', 'AMSynth',
         {'harmonicity': 0.25,
          'envelope': {'attack': 0.005, 'decay': 0.5, 'sustain': 0.1, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(4.0, 0.7, 0.05), _dist(0.4, 0.4)],
         ['Eb3',_N,_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,_N,_N,_N,
          'Eb3',_N,_N,_N,_N,_N,_N,_N,'Bb2',_N,_N,_N,_N,_N,_N,_N]),
    # Dissonant tritone motif — C and F# alternating (maximum tension)
    _cfg('tritone', 'lead', -21, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 18,
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.04, 'release': 0.35},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.06, 'release': 0.28}},
         [_dist(0.6, 0.5), _reverb(2.2, 0.4)],
         ['C4',_N,_N,'F#4',_N,_N,_N,_N,'C4',_N,'F#4',_N,_N,_N,_N,_N,
          'C4',_N,_N,_N,'F#4',_N,'C4',_N,_N,_N,_N,'F#4',_N,_N,_N,_N]),
    # Phrygian dark phrase — Ab/Eb area, thinned for negative space
    _cfg('phrygian_lead', 'lead', -15, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 15,
          'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_reverb(1.5, 0.35, 0.01), _dist(0.3, 0.3)],
         ['Ab4',_N,_N,_N,_N,_N,'G4',_N,'Eb4',_N,_N,_N,_N,_N,_N,_N,
          'Ab4',_N,_N,'Bb4',_N,_N,_N,_N,'Eb4',_N,_N,_N,'G4',_N,_N,_N]),
    # Locrian fragment — Bb Locrian sparse statement, maximum breathing room
    _cfg('locrian', 'lead', -14, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 18,
          'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_dist(0.6, 0.5), _reverb(2.0, 0.4)],
         ['Bb3',_N,_N,_N,_N,_N,'B3',_N,'Bb3',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'Db4',_N,_N,_N,_N,_N,'Ab3',_N,_N,_N,'Gb3',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# PSY ACCENTS — rhythmic punctuation only; used at most once per track.
# Dense-then-silent bursts that interrupt the space without filling it.
# Pure rhythmic role: short decays, no sustained atmospheric tail.
# ---------------------------------------------------------------------------
_PSY_ACCENTS = [
    # Glitch burst — dense cluster then long silence
    _cfg('glitch', 'lead', -20, '32n', 'FMSynth',
         {'harmonicity': 7, 'modulationIndex': 40,
          'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.03},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0.0, 'release': 0.02}},
         [_dist(0.8, 0.65)],
         ['Eb4','F4','E4','Eb4','Bb3','Eb4',_N,'F4',_N,_N,_N,_N,_N,_N,_N,_N,
          'Eb4','E4',_N,'Bb3',_N,_N,_N,'Eb4',_N,_N,_N,_N,_N,_N,_N,_N]),
    # Alien stutter — single note obsessively repeated, rhythmic identity only
    _cfg('stutter', 'lead', -21, '16n', 'FMSynth',
         {'harmonicity': 8, 'modulationIndex': 22,
          'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.02, 'release': 0.2},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.01, 'release': 0.15}},
         [_delay('16n', 0.5, 0.35), _dist(0.5, 0.45)],
         ['Eb4',_N,'Eb4',_N,_N,'Eb4',_N,_N,'Eb4',_N,_N,_N,'Eb4',_N,'Eb4',_N,
          'Eb4',_N,_N,'Eb4',_N,_N,_N,_N,'Eb4',_N,'Eb4',_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# MODULATION LAYERS — exactly one per track; purely atmospheric with movement.
# Automation-driven: the interest comes from motion, not rhythm or harmony.
# ---------------------------------------------------------------------------
_MOD_LAYERS = [
    # Dark AMSynth drone — creeping chromatic movement bar-to-bar
    _cfg('dark_drone', 'pad', -24, '16n', 'AMSynth',
         {'harmonicity': 0.1,
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.6, 'release': 3.0},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.5, 'release': 2.0}},
         [_reverb(8.0, 0.95), _dist(0.3, 0.25)],
         ['Ab1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Resonant bandpass sweep — noise through filter swept by automation
    _cfg('res_sweep', 'pad', -21, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.6, 'release': 1.5}},
         [_filt('bandpass', 400, 18), _reverb(3.0, 0.6), _dist(0.15, 0.2)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 150, 3500, 'tri')]),
    # Psychoacoustic beating — AM harmonicity creates slow amplitude flutter
    _cfg('beating', 'pad', -25, '16n', 'AMSynth',
         {'harmonicity': 0.05,
          'envelope': {'attack': 1.5, 'decay': 0.5, 'sustain': 0.8, 'release': 3.0},
          'modulationEnvelope': {'attack': 2.0, 'decay': 0.5, 'sustain': 0.7, 'release': 3.0}},
         [_reverb(10.0, 0.98), _dist(0.1, 0.15)],
         ['E1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'Eb1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=4),
    # Dark pad — FMSynth with filter sweep, Phrygian harmonic color
    _cfg('dark_pad', 'pad', -20, '2n', 'FMSynth',
         {'harmonicity': 0.2, 'modulationIndex': 15,
          'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.5, 'release': 2.5},
          'modulationEnvelope': {'attack': 1.5, 'decay': 0.5, 'sustain': 0.4, 'release': 2.0}},
         [_reverb(6.0, 0.85), _dist(0.2, 0.2), _filt('lowpass', 1500, 2)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:2:frequency', 400, 2500, 'tri')]),
]

# ---------------------------------------------------------------------------
# AMBIENT LAYERS — optional static atmosphere; added behind everything else.
# No rhythmic pattern, no melodic identity — pure space and subfrequency fill.
# ---------------------------------------------------------------------------
_AMBIENT_LAYERS = [
    # Pink noise drone — very slow attack, background wash
    _cfg('drone', 'pad', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.3, 'release': 2.0}},
         [_reverb(6.0, 0.9), _dist(0.2, 0.3)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    # Sub-bass FM drone — ultra-low, fills subfrequency space
    _cfg('sub_drone', 'pad', -18, '2n', 'FMSynth',
         {'harmonicity': 0.08, 'modulationIndex': 60,
          'envelope': {'attack': 0.5, 'decay': 0.8, 'sustain': 0.7, 'release': 2.5},
          'modulationEnvelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.5, 'release': 2.0}},
         [_reverb(4.0, 0.6), _filt('lowpass', 80, 1)],
         ['A0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'Ab0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    # Sparse alien event — rare AMSynth pings with very long reverb
    _cfg('alien_ping', 'pad', -23, '16n', 'AMSynth',
         {'harmonicity': 0.3,
          'envelope': {'attack': 0.005, 'decay': 0.6, 'sustain': 0.0, 'release': 0.8},
          'modulationEnvelope': {'attack': 0.4, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5}},
         [_reverb(7.0, 0.85, 0.1), _dist(0.3, 0.25)],
         [_N,_N,_N,_N,_N,_N,_N,_N,'Eb2',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'D2',_N,_N,_N],
         dropout_prob=0.3),
    # White noise background wash — constant dark texture under everything
    _cfg('noise_wash', 'pad', -28, '4n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 2.0, 'decay': 0.5, 'sustain': 0.5, 'release': 3.0}},
         [_filt('lowpass', 1200, 1), _reverb(8.0, 0.9), _dist(0.1, 0.1)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
]


# ---------------------------------------------------------------------------
# SUB — deep sine drone under the bassline. Role 'sub' bypasses sidechain so
# the low end never disappears under the kick — gives dark psy its constant low pressure.
# ---------------------------------------------------------------------------
_SUBS = [
    _cfg('sub', 'sub', -9, '2n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.01, 'decay': 0.5, 'sustain': 0.95, 'release': 0.4}},
         [_filt('lowpass', 120, 1)],
         ['A0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('sub', 'sub', -9, '2n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.01, 'decay': 0.55, 'sustain': 0.95, 'release': 0.45}},
         [_filt('lowpass', 110, 1)],
         ['E0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'D0',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# FILLS — sparse FX flourishes every 8-16 bars to break the hypnotic repetition.
# ---------------------------------------------------------------------------
_FILLS = [
    # Reverse-FX wash — every 16 bars
    _cfg('fill_wash', 'perc', -14, '2n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.4, 'decay': 0.1, 'sustain': 0.9, 'release': 0.2}},
         [_reverb(3.0, 0.7), _filt('bandpass', 1200, 4)],
         ['C3'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=7),
    # Dark metallic crash on bar 2 beat 1 — every 8 bars
    _cfg('fill_crash', 'perc', -12, '2n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.6, 'release': 0.5},
          'harmonicity': 6.5, 'modulationIndex': 38, 'resonance': 3500, 'octaves': 1.6},
         [_dist(0.5, 0.5), _reverb(2.5, 0.6)],
         [_N]*16 + ['C4'] + [_N]*15,
         loop_modulo=4, loop_modulo_remainder=3),
    # Sub bass impact on phrase start — every 16 bars, fires on loop 0 mod 8
    _cfg('fill_impact', 'perc', -8, '1n', 'MembraneSynth',
         {'pitchDecay': 0.15, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 1.0, 'sustain': 0.1, 'release': 1.5}},
         [_reverb(2.5, 0.55), _filt('lowpass', 400, 1.5)],
         ['C1'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=0),
]


class DarkPsyTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.DARK_PSY
    BPM_RANGE = (148, 152)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        # Foundation — always present
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.28, ghost_prob=0.1)
        layers = [kick, bass]

        # Rhythmic layer — hi-hat, present in most tracks
        if random.random() < 0.75:
            hihat = copy.deepcopy(cls._pick(_HIHATS))
            hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
            layers.append(hihat)

        # Core psy motif — exactly one; defines the harmonic/tonal identity
        motif = copy.deepcopy(cls._pick(_PSY_MOTIFS))
        motif['pattern']['velocities'] = _vel(motif['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
        layers.append(motif)

        # Modulation layer — exactly one; provides atmospheric movement via automation
        mod = copy.deepcopy(cls._pick(_MOD_LAYERS))
        layers.append(mod)

        # Sub drone — ultra-deep sine layer, present on most tracks for low-end weight
        if random.random() < 0.75:
            sub = copy.deepcopy(cls._pick(_SUBS))
            layers.append(sub)

        # Background ambient — optional static atmosphere (~60% of tracks)
        if random.random() < 0.6:
            ambient = copy.deepcopy(cls._pick(_AMBIENT_LAYERS))
            layers.append(ambient)

        # Rhythmic accent — ghost perc or psy accent, never both (~50% of tracks)
        if random.random() < 0.5:
            if random.random() < 0.5:
                ghost = copy.deepcopy(cls._pick(_GHOST_PERCS))
                ghost['pattern']['velocities'] = _vel(ghost['pattern']['steps'], accent_prob=0.15, ghost_prob=0.3)
                layers.append(ghost)
            else:
                accent = copy.deepcopy(cls._pick(_PSY_ACCENTS))
                accent['pattern']['velocities'] = _vel(accent['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
                layers.append(accent)

        # Phrase fill — FX wash / crash / impact every 8-16 bars to break the hypnotic loop
        if random.random() < 0.55:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _auto, _pingpong, _vel,
    _vel_groove, _vel_kick, _vel_snare, _four, _roll, _phrase,
)


# ---------------------------------------------------------------------------
# PATTERN BUILDERS — the psy grammar written once. The hi-tech and suomisaundi
# generators import these too, so every psy genre spells its kick and rolling
# bass the same way.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# KICKS — hard, strictly four-on-the-floor, short enough that the body is gone
# before the bass's first 16th. The base adds saturation to any kick without
# its own distortion; the ones below that carry one are the crunchier takes.
# ---------------------------------------------------------------------------
_KICKS = [
    # Tight punch: quick pitch drop, cut after a 16th so the roll starts in silence
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0, 'release': 0.05}},
         [], _four('G1')),
    # Crunch: hotter drive, the top tamed so it thuds rather than fizzes
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0, 'release': 0.04}},
         [_dist(0.6, 0.5), _filt('lowpass', 3500, 0.7)], _four('F1')),
    # Boomy: slower sweep and a lower tuning for the deeper night-time tracks
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0, 'release': 0.06}},
         [], _four('E1')),
    # Knock: high-tuned and dry, all attack
    _cfg('kick', 'kick', 1, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.04}},
         [_dist(0.4, 0.4)], _four('A1')),
    # Grinder: wide pitch sweep pushed through heavy distortion
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.028, 'octaves': 9,
          'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0, 'release': 0.04}},
         [_dist(0.85, 0.55), _filt('lowpass', 4000, 0.7)], _four('G1')),
    # Round: a touch longer and softer-edged
    _cfg('kick', 'kick', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0, 'release': 0.05}},
         [], _four('F#1')),
]

# ---------------------------------------------------------------------------
# BASSES — the genre. Every beat is K-B-B-B: silent on the kick's 16th, three
# very short notes after it. The rhythm never changes; the character comes from
# the notes (b2 grinds, tritones, semitone crawls, octave flicks) and from a
# resonant filter swept across each loop on top of the per-note filter snap.
# All written on A1 so key coherence keeps them between E1 and D#2.
# ---------------------------------------------------------------------------
_SQUELCH_SAW = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'type': 'lowpass', 'Q': 6, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.075, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 110, 'octaves': 4.5},
}
_GRIND_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'type': 'lowpass', 'Q': 8, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 90, 'octaves': 5},
}
# Sub-octave modulator: each note opens with a growling FM bite that dies within the 16th
_FM_GROWL = {
    'harmonicity': 0.5, 'modulationIndex': 22,
    'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.03},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.03},
}
# Forest voices: more resonance and a slower filter snap, so each note "talks" (squelch) instead of growling
_RUBBER_SAW = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'type': 'lowpass', 'Q': 12, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 140, 'octaves': 4},
}
_WET_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'type': 'lowpass', 'Q': 14, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.085, 'sustain': 0, 'release': 0.03},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.03,
                       'baseFrequency': 160, 'octaves': 3.5},
}
_FM_BLOOP = {
    'harmonicity': 1, 'modulationIndex': 10,
    'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.03},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03},
}

# Dark: heavy distortion into a resonant low-pass that sweeps open and shut over the loop
_DARK_BASSES = [
    # Phrygian rattle — b2 flicks at the end of beats, a leading-tone grind into the loop
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _SQUELCH_SAW,
         [_dist(0.8, 0.6), _filt('lowpass', 900, 5)],
         _roll('A1 A1 A1', 'A1 A1 Bb1', 'A1 A1 A1', 'A1 A2 A1',
               'A1 A1 A1', 'A1 A1 Bb1', 'A1 A1 A1', 'Bb1 A1 G#1'),
         automation=[_auto('effect:1:frequency', 300, 2600, 'tri')]),
    # Semitone crawl — a bar of root, then the line creeps up a half-step per beat and falls back
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.75, 0.55), _filt('lowpass', 800, 6)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1',
               'A1 A1 A1', 'Bb1 Bb1 Bb1', 'B1 B1 B1', 'C2 B1 Bb1'),
         automation=[_auto('effect:1:frequency', 250, 2400, 'tri')]),
    # Tritone answer — the root rolls, the flattened fifth answers at the end of each bar
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _GRIND_SQUARE,
         [_dist(0.9, 0.6), _filt('lowpass', 700, 7)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1', 'Eb2 Eb2 Eb2',
               'A1 A1 A1', 'A1 A1 A1', 'Eb2 D2 Eb2', 'A1 A1 -'),
         automation=[_auto('effect:1:frequency', 220, 2800, 'ramp')]),
    # b2 shudder — the middle 16th grinds a semitone up, bar 2 lurches up to the b6 and fifth
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _SQUELCH_SAW,
         [_dist(0.85, 0.6), _filt('lowpass', 850, 6)],
         _roll('A1 Bb1 A1', 'A1 A1 A1', 'A1 Bb1 A1', 'A1 A1 A1',
               'A1 Bb1 A1', 'A1 A1 A1', 'F2 F2 F2', 'E2 F2 E2'),
         automation=[_auto('effect:1:frequency', 280, 2500, 'tri')]),
    # Octave flick — the last 16th of every other beat jumps up, a b2 lift before the turn
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.7, 0.55), _filt('lowpass', 900, 5)],
         _roll('A1 A1 A2', 'A1 A1 A1', 'A1 A1 A2', 'A1 A1 A1',
               'A1 A1 A2', 'A1 A1 A1', 'Bb1 Bb1 Bb2', 'A1 A1 A1'),
         automation=[_auto('effect:1:frequency', 300, 3000, 'tri')]),
    # Diminished stairs — minor thirds stacked above the root, a flat-fifth slip at the loop end
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _GRIND_SQUARE,
         [_dist(0.85, 0.6), _filt('lowpass', 750, 7)],
         _roll('A1 A1 A1', 'A1 A1 C2', 'A1 A1 A1', 'A1 A1 Eb2',
               'A1 A1 A1', 'A1 A1 C2', 'A1 A1 A1', 'Gb1 Gb1 G#1'),
         automation=[_auto('effect:1:frequency', 200, 2400, 'ramp')]),
]

# Forest: less drive, more resonance — the roll bubbles and talks, with more movement inside each beat
_FOREST_BASSES = [
    # Tweak roll — minor-third and b2 flicks inside the beats, a chromatic wiggle on the turn
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _RUBBER_SAW,
         [_dist(0.45, 0.4), _filt('lowpass', 800, 8)],
         _roll('A1 A1 C2', 'A1 A1 A1', 'A1 Bb1 A1', 'A1 A1 G1',
               'A1 A1 C2', 'A1 A1 A1', 'A1 Bb1 A1', 'G1 G#1 G1'),
         automation=[_auto('effect:1:frequency', 260, 2000, 'tri')]),
    # Bubbling octave — the middle 16th pops an octave up, like something surfacing
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_BLOOP,
         [_dist(0.4, 0.35), _filt('lowpass', 900, 9)],
         _roll('A1 A2 A1', 'A1 A1 A1', 'A1 A2 A1', 'A1 A1 E2',
               'A1 A2 A1', 'A1 A1 A1', 'A1 A2 A1', 'Bb1 A1 G1'),
         automation=[_auto('effect:1:frequency', 300, 2200, 'tri')]),
    # Phrygian bounce — each off-beat opens on the b2 and falls back, a stepwise run home
    _cfg('bass', 'bass', -6, '16n', 'MonoSynth', _WET_SQUARE,
         [_dist(0.5, 0.4), _filt('lowpass', 700, 10)],
         _roll('A1 A1 A1', 'Bb1 A1 A1', 'A1 A1 A1', 'C2 Bb1 A1',
               'A1 A1 A1', 'Bb1 A1 A1', 'A1 A1 A1', 'D2 C2 Bb1'),
         automation=[_auto('effect:1:frequency', 240, 1900, 'tri')]),
    # Sinking crawl — a bar of root, then the floor drops a semitone at a time
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _RUBBER_SAW,
         [_dist(0.5, 0.45), _filt('lowpass', 850, 8)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1',
               'A1 A1 A1', 'A1 A1 A1', 'G#1 G#1 G#1', 'G1 G1 G#1'),
         automation=[_auto('effect:1:frequency', 280, 2300, 'ramp')]),
    # Call and answer — one dropped 16th leaves a hiccup, the answer leans on b2 and minor third
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_BLOOP,
         [_dist(0.45, 0.4), _filt('lowpass', 800, 9)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'A1 C2 A1', 'A1 - A1',
               'A1 A1 A1', 'A1 A1 A1', 'Bb1 C2 Bb1', 'A1 A1 A1'),
         automation=[_auto('effect:1:frequency', 260, 2100, 'tri')]),
]

# ---------------------------------------------------------------------------
# HI-HATS — shared by both flavours: off-beat "ts", busy 16ths, distorted
# hiss. _vel_groove adds the accent shape at generation time.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Off-beat open-ish hat — the classic psy "ts" between kicks
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.02},
          'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 5500, 'octaves': 1.5},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Straight 16ths — dense, driving
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 5800, 'octaves': 1.5},
         [],
         ['C4'] * 32),
    # Distorted noise hiss on every 16th off-beat
    _cfg('hihat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_dist(0.6, 0.55), _filt('highpass', 6000, 0.8)],
         [_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',
          _N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4']),
    # Off-beat with a pickup 16th — "ts-tk" pairs push into the next kick
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.5},
         [],
         [_N,_N,'C4','C4',_N,_N,'C4',_N,_N,_N,'C4','C4',_N,_N,'C4',_N,
          _N,_N,'C4','C4',_N,_N,'C4',_N,_N,_N,'C4','C4',_N,_N,'C4','C4']),
    # Sparse, breathing — gaps that let the forest textures through
    _cfg('hihat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 4000, 1)],
         [_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,_N,
          _N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,'C4',_N,_N,'C4']),
    # Low metallic 8ths — darker, heavier hat
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 240, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.015},
          'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 4800, 'octaves': 1.4},
         [_dist(0.3, 0.3)],
         [_N,_N,'C4',_N,'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,'C4',_N,
          _N,_N,'C4',_N,'C4',_N,'C4',_N,_N,_N,'C4',_N,'C4',_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# SNARES — optional; a crisp hit with the kick on 2 and 4.
# ---------------------------------------------------------------------------
_SNARES = [
    _cfg('snare', 'snare', -13, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.05}},
         [_filt('highpass', 1200, 0.8), _reverb(1.2, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Same backbeat with a ghost flam before the loop turns
    _cfg('snare', 'snare', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [_filt('highpass', 1500, 1), _dist(0.3, 0.25)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
]

# ---------------------------------------------------------------------------
# DARK MOTIFS — one per dark track. Dissonance is the point: tritones, b2s and
# clustered FM stabs, placed sparsely so silence does half the work. Each is
# written with A as its most frequent note so key coherence lines it up with
# the bass root rather than moving the tension around.
# ---------------------------------------------------------------------------
_DARK_MOTIFS = [
    # FM shriek — piercing high hits, a tritone and a b2 as the only departures
    _cfg('shriek', 'lead', -21, '16n', 'FMSynth',
         {'harmonicity': 12, 'modulationIndex': 28,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.08}},
         [_dist(0.7, 0.6), _reverb(1.4, 0.35, 0.01)],
         [_N,_N,'A5',_N,_N,_N,_N,_N,'Eb6',_N,_N,_N,_N,'A5',_N,_N,
          _N,_N,_N,_N,'A5',_N,_N,_N,'Bb5',_N,_N,_N,_N,_N,'A5',_N]),
    # Horror stab — clustered FM chords (root, b2, tritone) hitting off the beat
    _cfg('horror_stab', 'stab', -19, '16n', 'PolySynth',
         {'oscillator': {'type': 'fmsawtooth', 'harmonicity': 1.5, 'modulationIndex': 4},
          'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0, 'release': 0.25}},
         [_dist(0.5, 0.4), _reverb(2.5, 0.45, 0.02)],
         [_N,_N,_N,_N,_N,_N,'A3,Bb3,Eb4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'A3,Bb3,Eb4',_N,_N,_N,'A3,C4,Eb4',_N,_N,_N,_N,_N]),
    # Tritone bell — root and flat fifth trading places, a b2 sigh before the turn
    _cfg('tritone_bell', 'lead', -20, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 18,
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.04, 'release': 0.35},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.06, 'release': 0.28}},
         [_dist(0.6, 0.5), _reverb(2.2, 0.4)],
         ['A4',_N,_N,'Eb5',_N,_N,_N,_N,'A4',_N,'Eb5',_N,_N,_N,_N,_N,
          'A4',_N,_N,_N,'Eb5',_N,'A4',_N,_N,_N,_N,_N,'Bb4',_N,'A4',_N]),
    # Phrygian phrase — slow, sparse, the b2 leaning on the root
    _cfg('phrygian_lead', 'lead', -17, '16n', 'FMSynth',
         {'harmonicity': 5, 'modulationIndex': 15,
          'envelope': {'attack': 0.005, 'decay': 0.35, 'sustain': 0.05, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.1, 'release': 0.3}},
         [_reverb(1.5, 0.35, 0.01), _dist(0.3, 0.3)],
         ['A4',_N,_N,_N,_N,_N,'Bb4',_N,'F4',_N,_N,_N,_N,_N,_N,_N,
          'A4',_N,_N,'C5',_N,_N,'Bb4',_N,'A4',_N,_N,_N,'E4',_N,_N,_N]),
    # Locrian whisper — low, breathy AM tones climbing to the flat fifth
    _cfg('locrian_whisper', 'lead', -17, '16n', 'AMSynth',
         {'harmonicity': 0.25,
          'envelope': {'attack': 0.01, 'decay': 0.4, 'sustain': 0.1, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.2, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(4.0, 0.6, 0.05), _dist(0.4, 0.35)],
         ['A3',_N,_N,_N,_N,_N,'Bb3',_N,'A3',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'C4',_N,_N,_N,_N,_N,'Eb4',_N,_N,_N,'A3',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# DARK ATMOSPHERES — exactly one per dark track: horror drones and noise
# sweeps. All motion comes from automation and reverb, none from rhythm.
# ---------------------------------------------------------------------------
_DARK_ATMOSPHERES = [
    # Horror drone — slow AM swell creeping up a semitone in bar 2
    _cfg('horror_drone', 'pad', -24, '16n', 'AMSynth',
         {'harmonicity': 0.1,
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.6, 'release': 3.0},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.5, 'release': 2.0}},
         [_reverb(8.0, 0.95), _dist(0.3, 0.25)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'Bb2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Resonant noise sweep — narrow band-pass dragged up and down the spectrum
    _cfg('noise_sweep', 'pad', -22, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.6, 'release': 1.5}},
         [_filt('bandpass', 400, 18), _reverb(3.0, 0.6), _dist(0.15, 0.2)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 150, 3500, 'tri')]),
    # Beating drone — near-zero AM harmonicity makes the tone flutter like a failing light
    _cfg('beating_drone', 'pad', -25, '16n', 'AMSynth',
         {'harmonicity': 0.05,
          'envelope': {'attack': 1.5, 'decay': 0.5, 'sustain': 0.8, 'release': 3.0},
          'modulationEnvelope': {'attack': 2.0, 'decay': 0.5, 'sustain': 0.7, 'release': 3.0}},
         [_reverb(10.0, 0.98), _dist(0.1, 0.15)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G#2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    # Alien pings — rare AM tones sinking into a long reverb, missing on some loops
    _cfg('alien_ping', 'pad', -23, '16n', 'AMSynth',
         {'harmonicity': 0.3,
          'envelope': {'attack': 0.005, 'decay': 0.6, 'sustain': 0, 'release': 0.8},
          'modulationEnvelope': {'attack': 0.4, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5}},
         [_reverb(7.0, 0.85, 0.1), _dist(0.3, 0.25)],
         [_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'Eb4',_N,_N,_N],
         dropout_prob=0.3),
]

# ---------------------------------------------------------------------------
# METAL PERCUSSION — dark flavour only: cold metallic hits and clicks in the
# gaps, short decays so they never smear the roll.
# ---------------------------------------------------------------------------
_METAL_PERCS = [
    # Dark bell-like clang, sparse
    _cfg('metal_hit', 'perc', -21, '16n', 'MetalSynth',
         {'frequency': 180, 'envelope': {'attack': 0.001, 'decay': 0.2, 'release': 0.08},
          'harmonicity': 3.1, 'modulationIndex': 18, 'resonance': 2600, 'octaves': 0.8},
         [_dist(0.25, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,
          _N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N]),
    # Anvil — low inharmonic strike, distorted
    _cfg('anvil', 'perc', -20, '16n', 'MetalSynth',
         {'frequency': 110, 'envelope': {'attack': 0.001, 'decay': 0.12, 'release': 0.05},
          'harmonicity': 5.1, 'modulationIndex': 30, 'resonance': 1800, 'octaves': 1.0},
         [_dist(0.6, 0.45)],
         [_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,
          _N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Click — bright noise transients through a high-pass
    _cfg('click', 'perc', -20, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.006, 'sustain': 0, 'release': 0.004}},
         [_filt('highpass', 7000, 3)],
         [_N,_N,'C4',_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N]),
    # Chain rattle — 32nd-note metallic bursts at the end of each bar
    _cfg('rattle', 'perc', -22, '32n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.005},
          'harmonicity': 7.1, 'modulationIndex': 44, 'resonance': 5000, 'octaves': 1.2},
         [_reverb(1.5, 0.3)],
         _phrase(64, (27, 'C4 C4 C4 C4'), (59, 'C4 C4 - C4 C4')),
         subdivision='32n'),
]

# ---------------------------------------------------------------------------
# FOREST TWEAKS — one per forest track: wet, squelchy, talking synth fragments
# flicking around the root. Resonant filters and delays make them feel alive
# rather than menacing.
# ---------------------------------------------------------------------------
_FOREST_TWEAKS = [
    # Squelch tweak — high-Q square blips thrown across the stereo field
    _cfg('squelch_tweak', 'lead', -17, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'filter': {'type': 'lowpass', 'Q': 14, 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.05,
                             'baseFrequency': 250, 'octaves': 4}},
         [_pingpong('8n', 0.35, 0.3)],
         [_N,_N,'A3','A3',_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'A3',_N,
          _N,_N,'A3','A3',_N,_N,'Bb3',_N,_N,_N,_N,_N,'E4',_N,'A3',_N]),
    # Bubble — FM blips with a fast modulation snap, like gas rising through water
    _cfg('bubble', 'lead', -18, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 14,
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.03}},
         [_delay('8n.', 0.4, 0.3), _reverb(2.0, 0.3)],
         [_N,'A4',_N,_N,_N,_N,'A5',_N,_N,'A4',_N,_N,_N,'E5',_N,_N,
          _N,'A4',_N,_N,_N,_N,'A5',_N,_N,'C5',_N,'A4',_N,_N,_N,_N]),
    # Acid chirp — saw fragments under a resonant filter that keeps opening
    _cfg('acid_chirp', 'lead', -18, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05,
                             'baseFrequency': 200, 'octaves': 3.5}},
         [_filt('lowpass', 1200, 8), _delay('16n', 0.3, 0.2)],
         [_N,_N,_N,'A3','A3','Bb3',_N,_N,_N,_N,_N,'A3','C4',_N,_N,_N,
          _N,_N,_N,'A3','A3','Bb3',_N,_N,_N,_N,'G3',_N,'A3',_N,_N,_N],
         automation=[_auto('effect:0:frequency', 400, 4000, 'tri')]),
    # Drip — a sine that glides down between notes, falling drops echoing off the canopy
    _cfg('drip', 'lead', -18, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'portamento': 0.03,
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [_pingpong('8n.', 0.4, 0.35), _reverb(2.5, 0.3)],
         [_N,_N,'A5','E5',_N,_N,_N,_N,_N,_N,'A5',_N,_N,_N,_N,_N,
          _N,_N,'A5','E5',_N,_N,_N,_N,_N,_N,'C6','A5',_N,_N,_N,_N]),
    # Wah tweak — AM tones through a band-pass that wobbles open and shut
    _cfg('wah_tweak', 'lead', -17, '16n', 'AMSynth',
         {'harmonicity': 1.5,
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0, 'release': 0.06},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_filt('bandpass', 900, 6), _delay('8n', 0.3, 0.2)],
         [_N,_N,'A3',_N,_N,'A3',_N,_N,_N,_N,'C4',_N,_N,'A3',_N,_N,
          _N,_N,'A3',_N,_N,'A3',_N,_N,_N,_N,'D4',_N,'C4',_N,'A3',_N],
         automation=[_auto('effect:0:frequency', 500, 2800, 'tri')]),
]

# ---------------------------------------------------------------------------
# FOREST TEXTURES — one per forest track: nature, not horror. Wind, drops,
# birds, an airy open-fifth canopy.
# ---------------------------------------------------------------------------
_FOREST_TEXTURES = [
    # Wind — pink noise through a slowly drifting band-pass
    _cfg('wind', 'pad', -22, '2n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}},
         [_filt('bandpass', 600, 3), _reverb(4.0, 0.6)],
         ['C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'C3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 300, 1500, 'tri')]),
    # Water drops — tiny membrane "bloips" at irregular spots, echoing
    _cfg('water_drops', 'pad', -20, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 1.5,
          'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [_pingpong('8n.', 0.35, 0.35), _reverb(2.5, 0.4)],
         [_N,_N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,_N,_N,'E5',_N,_N,
          _N,_N,_N,_N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,_N,'C6',_N],
         sidechain='shallow'),
    # Canopy — an airy open fifth, chorused, no dissonance
    _cfg('canopy', 'pad', -24, '1n', 'AMSynth',
         {'harmonicity': 2,
          'envelope': {'attack': 1.2, 'decay': 0.5, 'sustain': 0.7, 'release': 2.5},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.6, 'release': 2.0}},
         [_chorus(1.5, 3.5, 0.6, 0.5), _reverb(6.0, 0.8)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Bird call — gliding high sine chirps, sparse and echoing, absent on some loops
    _cfg('bird_call', 'pad', -23, '16n', 'Synth',
         {'oscillator': {'type': 'sine'}, 'portamento': 0.04,
          'envelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_delay('8n.', 0.3, 0.25), _reverb(3.0, 0.4)],
         [_N,_N,_N,_N,_N,_N,'E6','A6',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A6','E6','A6',_N,_N,_N],
         dropout_prob=0.3, sidechain='shallow'),
]

# ---------------------------------------------------------------------------
# WOOD PERCUSSION — forest flavour, always one: tuned toms and wood-block
# clicks, the organic tribal layer that marks forest psy.
# ---------------------------------------------------------------------------
_WOOD_PERCS = [
    # Tuned toms — a three-pitch tribal phrase answering the kick
    _cfg('tribal_toms', 'perc', -16, '16n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 2.5,
          'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.1}},
         [_reverb(1.2, 0.2)],
         [_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N,'B2',_N,
          _N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,'G3',_N,_N,'B2',_N]),
    # Wood clicks — near-instant membrane "toks", syncopated
    _cfg('wood_clicks', 'perc', -17, '32n', 'MembraneSynth',
         {'pitchDecay': 0.004, 'octaves': 1.2,
          'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.02}},
         [],
         [_N,_N,_N,'E5',_N,_N,'E5',_N,_N,_N,_N,'B5',_N,_N,_N,_N,
          _N,_N,_N,'E5',_N,_N,'E5',_N,_N,_N,_N,'B5',_N,_N,'E5',_N]),
    # Log drum — low hollow knocks rolling into each bar line
    _cfg('log_drum', 'perc', -16, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 2,
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_filt('lowpass', 2500, 1)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A2','A2','E2',
          _N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,'A2','E2','E2']),
    # Seed shaker — band-passed noise ticks in a skipping pattern
    _cfg('seed_shaker', 'perc', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.025, 'sustain': 0, 'release': 0.015}},
         [_filt('bandpass', 2500, 6)],
         [_N,'C4',_N,'C4',_N,'C4','C4',_N,_N,'C4',_N,'C4',_N,'C4',_N,_N,
          _N,'C4',_N,'C4',_N,'C4','C4',_N,_N,'C4',_N,_N,_N,'C4','C4','C4']),
]

# ---------------------------------------------------------------------------
# FOREST GLITCHES — optional extra on forest tracks: short 32nd-note FX bursts
# in a few spots across the two bars, silent everywhere else.
# ---------------------------------------------------------------------------
_FOREST_GLITCHES = [
    # FM zap bursts at the end of beats
    _cfg('glitch_burst', 'perc', -21, '32n', 'FMSynth',
         {'harmonicity': 7, 'modulationIndex': 40,
          'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.02},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_dist(0.5, 0.4)],
         _phrase(64, (12, 'A5 A5 E5 A5'), (44, 'A5 - A5 A5'), (58, 'E5 A5 C6 A5 E5 A5')),
         subdivision='32n'),
    # Twig snaps — dry metallic crackle in pairs
    _cfg('twig_snap', 'perc', -22, '32n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.008, 'release': 0.004},
          'harmonicity': 3.7, 'modulationIndex': 24, 'resonance': 4000, 'octaves': 0.6},
         [],
         _phrase(64, (5, 'C4 C4'), (21, 'C4 - C4'), (37, 'C4 C4'), (53, 'C4 C4 C4 - C4')),
         subdivision='32n'),
    # Bleep scatter — lone square blips bouncing in a ping-pong delay
    _cfg('bleep_scatter', 'perc', -22, '32n', 'Synth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_pingpong('16n', 0.4, 0.4), _filt('lowpass', 5000, 1)],
         _phrase(64, (6, 'A6'), (19, 'E6 A6'), (38, 'A6'), (51, 'C7 A6'), (62, 'E6')),
         subdivision='32n'),
]

# ---------------------------------------------------------------------------
# FILLS — sparse phrase markers every 8-16 bars to break the hypnosis.
# ---------------------------------------------------------------------------
_FILLS = [
    # Reverse-style noise swell into the phrase — every 8 loops
    _cfg('fill_wash', 'perc', -15, '2n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.4, 'decay': 0.1, 'sustain': 0.9, 'release': 0.2}},
         [_reverb(3.0, 0.7), _filt('bandpass', 1200, 4)],
         ['C3'] + [_N] * 31,
         loop_modulo=8, loop_modulo_remainder=7),
    # Metallic crash on bar 2 — every 4 loops
    _cfg('fill_crash', 'perc', -14, '2n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.6, 'release': 0.5},
          'harmonicity': 6.5, 'modulationIndex': 38, 'resonance': 3500, 'octaves': 1.6},
         [_dist(0.5, 0.5), _reverb(2.5, 0.6)],
         [_N] * 16 + ['C4'] + [_N] * 15,
         loop_modulo=4, loop_modulo_remainder=3),
    # Low impact on the phrase start — every 8 loops
    _cfg('fill_impact', 'perc', -10, '1n', 'MembraneSynth',
         {'pitchDecay': 0.15, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 1.0, 'sustain': 0.1, 'release': 1.5}},
         [_reverb(2.5, 0.55), _filt('lowpass', 400, 1.5)],
         ['C1'] + [_N] * 31,
         loop_modulo=8, loop_modulo_remainder=0),
]


class DarkPsyTrackGenerator(BaseTrackGenerator):
    """Dark and forest psy, one genre with two flavours. They share the kick, the hats and the rolling
    K-B-B-B bass grammar; the flavour picks the bass voice and everything around it."""
    GENRE = GenreType.DARK_PSY
    BPM_RANGE = (148, 158)
    LEVEL_DB = -2.5
    PROFILE = GenreProfile(
        drums='Hard, distorted four-on-the-floor kick; woody percussion in the forest flavour',
        bass='Rolling K-B-B-B, very short, distorted and squelchy, crawling chromatically',
        signature='Horror drones and metallic hits (dark), or wet glitches and nature sounds (forest)',
        mood='Dark, alien, intense',
        key_trait='bass',
        kick_pattern='four',
        bass_pattern='rolling',
    )
    KEY_ROLES = ('bass',)
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.18

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        forest = random.random() < 0.5

        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_FOREST_BASSES if forest else _DARK_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        # No ghost notes: a quiet 16th reads as a hole in the roll
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        layers = [kick, bass, hihat]

        motif = copy.deepcopy(cls._pick(_FOREST_TWEAKS if forest else _DARK_MOTIFS))
        motif['pattern']['velocities'] = _vel(motif['pattern']['steps'], accent_prob=0.25, ghost_prob=0.05)
        if random.random() < 0.35:
            motif['entry_loop'] = 2
        layers.append(motif)

        atmosphere = copy.deepcopy(cls._pick(_FOREST_TEXTURES if forest else _DARK_ATMOSPHERES))
        atmosphere['pattern']['velocities'] = _vel(atmosphere['pattern']['steps'], accent_prob=0.2, ghost_prob=0.1)
        layers.append(atmosphere)

        if forest:
            wood = copy.deepcopy(cls._pick(_WOOD_PERCS))
            wood['pattern']['velocities'] = _vel(wood['pattern']['steps'], accent_prob=0.25, ghost_prob=0.2)
            layers.append(wood)
            glitch = cls._maybe(_FOREST_GLITCHES, 0.5)
            if glitch is not None:
                glitch = copy.deepcopy(glitch)
                glitch['pattern']['velocities'] = _vel(glitch['pattern']['steps'], accent_prob=0.3, ghost_prob=0.15)
                layers.append(glitch)
        else:
            metal = cls._maybe(_METAL_PERCS, 0.7)
            if metal is not None:
                metal = copy.deepcopy(metal)
                metal['pattern']['velocities'] = _vel(metal['pattern']['steps'], accent_prob=0.2, ghost_prob=0.25)
                layers.append(metal)

        snare = cls._maybe(_SNARES, 0.35)
        if snare is not None:
            snare = copy.deepcopy(snare)
            snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
            layers.append(snare)

        fill = cls._maybe(_FILLS, 0.5)
        if fill is not None:
            layers.append(copy.deepcopy(fill))

        cls._apply_key_coherence(layers)
        return layers

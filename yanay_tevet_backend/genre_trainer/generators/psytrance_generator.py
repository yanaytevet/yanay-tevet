import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _auto,
    _vel, _vel_groove, _vel_kick,
)

# ---------------------------------------------------------------------------
# KICKS — driving 4/4 with deep sub tail (the "psy thump").
# Short pitchDecay and high octaves give the characteristic pitched click.
# ---------------------------------------------------------------------------
_KICKS = [
    # Standard 4/4 — clean punchy
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.4}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Slightly distorted, deep tail
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.18, 0.25)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Deep dub-style — longer pitch decay, less click
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.7}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Long reverb tail kick — early track / breakdown style
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 2.0}},
         [_reverb(1.2, 0.15)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Punchy click — short decay, high octaves
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Anticipation hit before bar-2 beat 1 (step 15)
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.3}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
    # Rolling double on beat 3
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.3}},
         [_dist(0.15, 0.22)],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# OFFBEAT BASSES — the defining sound of psytrance.
# Bass plays *between* kicks (steps 2,6,10,14 = "and" of each beat) to create
# the rolling 1-AND-3-AND "duf-duf-duf" pulse. Rest pattern is sparse and tight.
# ---------------------------------------------------------------------------
_FM_PSY = {
    'harmonicity': 0.5, 'modulationIndex': 18,
    'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.0, 'release': 0.08},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.08},
}
_MONO_PSY = {
    'oscillator': {'type': 'sawtooth'},
    'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.0, 'release': 0.06},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.06,
                       'baseFrequency': 200, 'octaves': 3.5},
}

_BASSES = [
    # Classic A minor offbeat — bass on 2,6,10,14 every bar
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_PSY,
         [_dist(0.4, 0.45), _filt('lowpass', 700, 4)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N],
         automation=[_auto('effect:1:frequency', 350, 1800, 'tri')]),
    # E Phrygian offbeat with chromatic colour
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_PSY,
         [_dist(0.45, 0.5), _filt('lowpass', 650, 5)],
         [_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,
          _N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N,'E1',_N,_N,_N,'F1',_N],
         automation=[_auto('effect:1:frequency', 300, 2000, 'tri')]),
    # D minor offbeat with octave jumps
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _MONO_PSY,
         [_dist(0.5, 0.5), _filt('lowpass', 600, 6)],
         [_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D2',_N,_N,_N,'D1',_N,
          _N,_N,'D1',_N,_N,_N,'F1',_N,_N,_N,'D2',_N,_N,_N,'C1',_N],
         automation=[_auto('effect:1:frequency', 280, 1900, 'tri')]),
    # G minor rolling offbeat with melodic answer in bar 2
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_PSY,
         [_dist(0.42, 0.45), _filt('lowpass', 720, 4)],
         [_N,_N,'G1',_N,_N,_N,'G1',_N,_N,_N,'G1',_N,_N,_N,'G1',_N,
          _N,_N,'G1',_N,_N,_N,'Bb1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N],
         automation=[_auto('effect:1:frequency', 320, 2100, 'tri')]),
    # F# minor — darker offbeat, occasional 16th passing note
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_PSY,
         [_dist(0.45, 0.48), _filt('lowpass', 680, 5)],
         [_N,_N,'F#1',_N,_N,_N,'F#1','G1',_N,_N,'F#1',_N,_N,_N,'F#1',_N,
          _N,_N,'F#1',_N,_N,_N,'E1','F#1',_N,_N,'G1',_N,_N,_N,'F#1',_N]),
    # B Phrygian — Phrygian dominant flavour, dense answer
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _MONO_PSY,
         [_dist(0.48, 0.5), _filt('lowpass', 640, 5)],
         [_N,_N,'B0',_N,_N,_N,'B0',_N,_N,_N,'C1',_N,_N,_N,'B0',_N,
          _N,_N,'B0',_N,_N,_N,'C1','B0',_N,_N,'D#1',_N,_N,_N,'B0',_N],
         automation=[_auto('effect:1:frequency', 250, 1700, 'tri')]),
    # A minor — punchy, occasional triplet feel on offbeats
    _cfg('bass', 'bass', -5, '16n', 'FMSynth', _FM_PSY,
         [_dist(0.5, 0.5), _filt('lowpass', 700, 6)],
         [_N,_N,'A1',_N,_N,_N,'A1','A1',_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'C2',_N,_N,_N,'A1',_N,_N,_N,'G1','A1']),
]

# ---------------------------------------------------------------------------
# HI-HATS — 16th open hat on the "and" or full 16ths; metallic shimmer.
# Velocities applied via _vel_groove for natural accent/ghost feel.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Open hat on every offbeat (8th notes)
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 400, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 4000, 'octaves': 1.5},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # 8th-note steady hat
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 5000, 'octaves': 1.2},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # Full 16ths — driving energy
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008},
          'harmonicity': 4.8, 'modulationIndex': 28, 'resonance': 4500, 'octaves': 1.3},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Syncopated metallic shimmer
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 450, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.012},
          'harmonicity': 5.2, 'modulationIndex': 33, 'resonance': 4300, 'octaves': 1.4},
         [],
         [_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,
          _N,'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N]),
    # Open hat — longer decay for "tss" sustain
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.18, 'release': 0.12},
          'harmonicity': 4.8, 'modulationIndex': 28, 'resonance': 4200, 'octaves': 1.4},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Triplet-feel groupings (3+3+2 over 16ths)
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.02, 'release': 0.01},
          'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 4600, 'octaves': 1.4},
         [],
         ['C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,
          'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N]),
]

# ---------------------------------------------------------------------------
# LEADS — call-and-response phrases over the rolling bass, A/E minor flavours.
# Reverb + delay creates the hypnotic stereo space typical of full-on.
# ---------------------------------------------------------------------------
_LEADS = [
    # A minor pentatonic — climbing and falling
    _cfg('lead', 'lead', -12, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(1.2, 0.35, 0.01), _delay('16n', 0.25, 0.15)],
         ['A4',_N,_N,'C5',_N,_N,'E5',_N,'D5',_N,_N,_N,'C5',_N,'A4',_N,
          'A4',_N,_N,'C5',_N,_N,'G5',_N,'E5',_N,_N,_N,'C5',_N,'A4',_N]),
    # E Phrygian ascending climax
    _cfg('lead', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.15, 'release': 0.4}},
         [_reverb(1.5, 0.3, 0.01), _delay('16n', 0.2, 0.12)],
         ['E5',_N,_N,'F5',_N,_N,'G5',_N,'F5',_N,_N,_N,'E5',_N,_N,_N,
          'D5',_N,_N,'E5',_N,_N,'G5',_N,'F5',_N,_N,_N,'G5',_N,'A5',_N]),
    # FM with mod index automation feel (filter sweep substitutes)
    _cfg('lead', 'lead', -13, '16n', 'FMSynth',
         {'harmonicity': 3, 'modulationIndex': 8,
          'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.3, 'release': 0.5}},
         [_reverb(1.2, 0.28, 0.01), _delay('8n', 0.18, 0.1), _filt('lowpass', 4000, 2)],
         ['A4',_N,_N,_N,'C5',_N,'E5',_N,'D5',_N,'C5',_N,_N,_N,'A4',_N,
          'G4',_N,_N,_N,'A4',_N,'C5',_N,'E5',_N,'G5',_N,'E5',_N,'D5',_N],
         automation=[_auto('effect:2:frequency', 800, 6000, 'tri')]),
    # AMSynth with slow modulation — Vini Vici style breathy lead
    _cfg('lead', 'lead', -13, '16n', 'AMSynth',
         {'harmonicity': 2,
          'envelope': {'attack': 0.008, 'decay': 0.3, 'sustain': 0.1, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.8, 'release': 0.4}},
         [_reverb(1.3, 0.32, 0.01), _delay('16n', 0.22, 0.12)],
         ['D5',_N,_N,'F5',_N,'A5',_N,_N,'G5',_N,_N,'F5','D5',_N,_N,_N,
          'D5',_N,'E5','F5','A5',_N,_N,'G5','F5','E5',_N,_N,'D5',_N,_N,_N]),
    # Rolling 16th lead — full-on driving
    _cfg('lead', 'lead', -11, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 12,
          'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.15, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.3, 'decay': 0.1, 'sustain': 0.6, 'release': 0.3}},
         [_reverb(1.5, 0.35, 0.02), _delay('16n', 0.18, 0.14), _filt('lowpass', 3500, 2.5)],
         ['A4',_N,_N,'C5',_N,'E5',_N,'D5','C5',_N,_N,'A4',_N,_N,'G4',_N,
          'A4',_N,'C5','E5',_N,'G5','F5','E5','D5','C5',_N,_N,'A4',_N,_N,_N],
         automation=[_auto('effect:2:frequency', 900, 5500, 'tri')]),
    # High register answer phrase — climactic
    _cfg('lead', 'lead', -11, '16n', 'FMSynth',
         {'harmonicity': 2.0, 'modulationIndex': 14,
          'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.12, 'release': 0.38},
          'modulationEnvelope': {'attack': 0.4, 'decay': 0.12, 'sustain': 0.5, 'release': 0.3}},
         [_reverb(1.6, 0.38, 0.02), _delay('16n', 0.2, 0.12)],
         ['G5',_N,_N,'Bb5',_N,'D6',_N,'C6','Bb5',_N,_N,'G5',_N,_N,'F5',_N,
          'G5',_N,'Bb5','D6',_N,'F6','Eb6','D6','C6','Bb5',_N,_N,'G5',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# PADS / ATMOS — slow harmonic foundation. Optional, used for the
# breakdown moments. Long reverb tails create the cosmic feeling.
# ---------------------------------------------------------------------------
_PADS = [
    # A minor / G slow pad
    _cfg('pad', 'pad', -16, '16n', 'AMSynth',
         {'harmonicity': 1.0,
          'envelope': {'attack': 0.5, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.8, 'release': 1.5}},
         [_reverb(4.0, 0.7)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    # E minor triangle pad — wide stereo
    _cfg('pad', 'pad', -18, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.9, 'release': 2.5}},
         [_reverb(5.0, 0.8), _chorus(0.5, 3, 0.4, 0.3)],
         ['E2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    # D minor with motion every half bar
    _cfg('pad', 'pad', -17, '16n', 'AMSynth',
         {'harmonicity': 0.5,
          'envelope': {'attack': 0.4, 'decay': 0.6, 'sustain': 0.75, 'release': 2.2},
          'modulationEnvelope': {'attack': 0.6, 'decay': 0.4, 'sustain': 0.7, 'release': 2.0}},
         [_reverb(4.5, 0.75)],
         ['D2',_N,_N,_N,_N,_N,_N,_N,'A2',_N,_N,_N,_N,_N,_N,_N,
          'D2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N]),
    # Sub drone — fills sub frequencies behind the bassline
    _cfg('sub_drone', 'pad', -20, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.9, 'release': 3.0}},
         [_reverb(6.0, 0.85), _filt('lowpass', 200, 1)],
         ['A1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'E1',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
]


# ---------------------------------------------------------------------------
# SUB — pure sine drone under the offbeat bass for additional weight.
# Role 'sub' bypasses sidechain so the low end stays solid under each kick.
# ---------------------------------------------------------------------------
_SUBS = [
    _cfg('sub', 'sub', -10, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.4, 'sustain': 0.9, 'release': 0.3}},
         [_filt('lowpass', 140, 1)],
         ['A0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N,
          'A0',_N,_N,_N,_N,_N,_N,_N,'A0',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('sub', 'sub', -10, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.45, 'sustain': 0.92, 'release': 0.3}},
         [_filt('lowpass', 130, 1)],
         ['E0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N,
          'D0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('sub', 'sub', -10, '4n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.004, 'decay': 0.42, 'sustain': 0.9, 'release': 0.3}},
         [_filt('lowpass', 150, 1)],
         ['F0',_N,_N,_N,_N,_N,_N,_N,'F0',_N,_N,_N,_N,_N,_N,_N,
          'G0',_N,_N,_N,_N,_N,_N,_N,'F0',_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# FILLS — phrase-level accents (uplifters, FX hits, snare rolls) every 8-16 bars.
# ---------------------------------------------------------------------------
_FILLS = [
    # White-noise uplifter into the next phrase — every 16 bars
    _cfg('fill_uplifter', 'perc', -12, '1n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.8, 'decay': 0.05, 'sustain': 0.95, 'release': 0.1}},
         [_reverb(1.0, 0.45), _filt('highpass', 1800, 1.3)],
         ['C3'] + [_N]*31,
         loop_modulo=8, loop_modulo_remainder=7),
    # Reverse-cymbal style swell — every 8 bars
    _cfg('fill_swell', 'perc', -14, '2n', 'MetalSynth',
         {'frequency': 350, 'envelope': {'attack': 1.0, 'decay': 0.3, 'release': 0.5},
          'harmonicity': 5.5, 'modulationIndex': 32, 'resonance': 4500, 'octaves': 1.6},
         [_reverb(2.0, 0.55)],
         [_N]*16 + ['C4'] + [_N]*15,
         loop_modulo=4, loop_modulo_remainder=3),
    # 16-step snare/FX roll on the final beat — every 16 bars
    _cfg('fill_roll', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.04}},
         [_reverb(0.6, 0.4), _filt('highpass', 1200, 1.5)],
         [_N]*28 + ['C3', 'C3', 'C3', 'C3'],
         loop_modulo=8, loop_modulo_remainder=7),
]


class PsytranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSYTRANCE
    BPM_RANGE = (145, 150)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        lead = copy.deepcopy(cls._pick(_LEADS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.18, ghost_prob=0.05)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.25, ghost_prob=0.08)

        # Lead may enter after the intro — adds arrangement variety
        if random.random() < 0.4:
            lead['entry_loop'] = random.choice([2, 4])

        layers = [kick, bass, hihat, lead]

        # Sub drone — present on most tracks, fills the bottom octave under the offbeat bass
        if random.random() < 0.7:
            sub = copy.deepcopy(cls._pick(_SUBS))
            sub['pattern']['velocities'] = _vel(sub['pattern']['steps'], accent_prob=0.05, ghost_prob=0.0)
            layers.append(sub)

        # Pad/atmosphere in roughly half of tracks
        if random.random() < 0.5:
            layers.append(copy.deepcopy(cls._pick(_PADS)))

        # Phrase fill — uplifter / swell / roll every 8-16 bars
        if random.random() < 0.55:
            layers.append(copy.deepcopy(cls._pick(_FILLS)))

        cls._apply_key_coherence(layers)
        return layers

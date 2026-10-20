import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _chorus, _filt, _delay, _pingpong, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare, _vel_rumble, _clear_kick_steps, _tune_kick,
)


# D1 (37 Hz) up to C#2 (69 Hz): a deep, round techno kick fundamental.
_KICK_LOWEST_MIDI = 26

# ---------------------------------------------------------------------------
# KICKS — round, punchy Berlin kick on every quarter. Only light saturation or
# room: in techno the weight comes from the kick + rumble together, not from a
# distorted kick (that is hard techno's cue). The note is a placeholder;
# _tune_kick retunes it to the track root.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.2}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Tight and punchy — a short sweep with a touch of saturation for the click
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.2, 0.25)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Warehouse room — longer body with a short room reverb
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.4}},
         [_reverb(1.2, 0.12)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Driving — saturated, with the fizz rolled off so it stays round
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.3, 0.3), _filt('lowpass', 5000, 0.7)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Extra 16th into the bar-2 downbeat — pushes the second bar
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.1}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1',
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Extra 16th into the loop restart
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 7.5, 'envelope': {'attack': 0.001, 'decay': 0.44, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.15, 0.2)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1']),
]

# ---------------------------------------------------------------------------
# RUMBLES — the modern techno low end: a low note on the three 16ths after
# every kick, smeared by a long reverb, distorted and lowpassed so only the
# sub growl is left. With the deep sidechain it reads as the kick's own tail
# rumbling between hits. Variety is in the source voice and the reverb/drive,
# never in the rhythm.
# ---------------------------------------------------------------------------
_RUMBLES = [
    # Kick-tail rumble — a dull membrane thump into reverb, then distortion (the classic chain)
    _cfg('rumble', 'bass', 0, '16n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 2.5, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.1}},
         [_reverb(4.0, 0.85, 0.01), _dist(0.55, 0.8), _filt('lowpass', 150, 1.0)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1'],
         sidechain='deep'),
    # Sine rumble with a slowly opening lowpass; drops a tone on the last beat
    _cfg('rumble', 'bass', -1, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0.25, 'release': 0.12},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.4, 'release': 0.1,
                             'baseFrequency': 70, 'octaves': 2}},
         [_dist(0.65, 0.7), _reverb(3.0, 0.7), _filt('lowpass', 160, 1.2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'G1','G1','G1'],
         automation=[_auto('effect:2:frequency', 120, 200, 'tri')],
         sidechain='deep'),
    # Dark, long-tailed rumble with a phrygian half-step lift at the end of each bar
    _cfg('rumble', 'bass', 1, '16n', 'MonoSynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0.15, 'release': 0.15},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.3, 'release': 0.1,
                             'baseFrequency': 60, 'octaves': 2}},
         [_reverb(5.5, 0.9), _dist(0.75, 0.75), _filt('lowpass', 125, 1.4)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'Bb1','Bb1','Bb1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'Bb1','Bb1','Bb1'],
         sidechain='deep'),
    # Gritty saw rumble — more drive, shorter room, so each 16th is just audible
    _cfg('rumble', 'bass', -2, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.2, 'release': 0.08},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.2, 'release': 0.08,
                             'baseFrequency': 80, 'octaves': 2}},
         [_dist(0.5, 0.6), _reverb(2.5, 0.65), _filt('lowpass', 200, 0.9)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'A1','A1','A1',_N,'A1','A1','A1',_N,'C2','C2','C2',_N,'C2','C2','C2'],
         sidechain='deep'),
]

# ---------------------------------------------------------------------------
# BASSES — the other techno low ends: the offbeat bass on the 3rd 16th of each
# beat ("doom-BA") and syncopated off-kick sequences. Never on the kick — the
# kick owns the downbeats; the bass answers it.
# ---------------------------------------------------------------------------
_BASSES = [
    # Classic offbeat saw bass, one note per offbeat, steps down at the end of the loop
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.14, 'sustain': 0.1, 'release': 0.08},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.1, 'release': 0.08,
                             'baseFrequency': 90, 'octaves': 3}},
         [_filt('lowpass', 900, 1.5)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N]),
    # Offbeat FM "bonk" with octave jumps
    _cfg('bass', 'bass', -6, '16n', 'FMSynth',
         {'harmonicity': 1, 'modulationIndex': 3.5,
          'oscillator': {'type': 'sine'}, 'modulation': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.18, 'sustain': 0, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_filt('lowpass', 700, 1)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A2',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'C2',_N,_N,_N,'A2',_N]),
    # Dark offbeat square with a filter that breathes over the loop
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.15, 'release': 0.08},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.15, 'release': 0.08,
                             'baseFrequency': 80, 'octaves': 2.5}},
         [_dist(0.35, 0.4), _filt('lowpass', 600, 2)],
         [_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,
          _N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N,_N,_N,'A1',_N],
         automation=[_auto('effect:1:frequency', 300, 1300, 'tri')]),
    # Galloping off-kick bass: the offbeat plus the 16th after it, octave on every other pair
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.05, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.05, 'release': 0.05,
                             'baseFrequency': 100, 'octaves': 3}},
         [_filt('lowpass', 1000, 1.2)],
         [_N,_N,'A1','A1',_N,_N,'A1','A2',_N,_N,'A1','A1',_N,_N,'A1','A2',
          _N,_N,'A1','A1',_N,_N,'A1','A2',_N,_N,'G1','G1',_N,_N,'G1','A2']),
    # Hypnotic syncopated sequence — rolls around the kick without touching it
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.1, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.1, 'release': 0.06,
                             'baseFrequency': 90, 'octaves': 3.2}},
         [_filt('lowpass', 800, 2.5)],
         [_N,_N,'A1','A1',_N,_N,'A1',_N,_N,_N,'A1','C2',_N,_N,'A1',_N,
          _N,_N,'A1','A1',_N,_N,'A1',_N,_N,'G1',_N,'A1',_N,_N,'A1',_N],
         automation=[_auto('effect:0:frequency', 400, 1600, 'tri')]),
    # Detroit-style minor sequence, higher up so the line itself is heard
    _cfg('bass', 'bass', -9, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.16, 'sustain': 0.2, 'release': 0.1},
          'filterEnvelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.15, 'release': 0.1,
                             'baseFrequency': 120, 'octaves': 3}},
         [_filt('lowpass', 1200, 2)],
         [_N,_N,_N,'E2',_N,_N,'E2',_N,_N,'G2',_N,_N,_N,_N,'E2',_N,
          _N,_N,_N,'E2',_N,_N,'D2',_N,_N,'E2',_N,'G2',_N,_N,'B1',_N]),
]

# ---------------------------------------------------------------------------
# CLOSED HATS — the 16th-note grid the offbeat open hat sits on top of.
# Velocities via _vel_groove so the 16ths breathe rather than machine-gun.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Straight 16ths
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 5200, 'octaves': 1.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 16ths that step aside on the offbeat for the open hat
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 480, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.01},
          'harmonicity': 4.8, 'modulationIndex': 30, 'resonance': 5000, 'octaves': 1.45},
         [],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4',
          'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4']),
    # Ride-like 16ths — longer, darker, quieter
    _cfg('hihat', 'hihat', -20, '16n', 'MetalSynth',
         {'frequency': 420, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.03},
          'harmonicity': 4.5, 'modulationIndex': 26, 'resonance': 3800, 'octaves': 1.3},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Skippy 16ths — gaps give the grid a lope
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.012},
          'harmonicity': 5.0, 'modulationIndex': 30, 'resonance': 6500, 'octaves': 1.6},
         [],
         ['C4','C4','C4',_N,'C4',_N,'C4','C4','C4','C4',_N,'C4','C4',_N,'C4','C4',
          'C4','C4','C4',_N,'C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4']),
    # Noise shaker 16ths — softer, analogue-drum-machine texture
    _cfg('hihat', 'hihat', -24, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.025, 'sustain': 0, 'release': 0.01}},
         [_filt('highpass', 8000, 0.8)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Gritty industrial 16ths
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.022, 'release': 0.01},
          'harmonicity': 5.8, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.7},
         [_dist(0.3, 0.3)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
]

# ---------------------------------------------------------------------------
# OPEN HATS — the techno signature: an open hat on every offbeat (the 3rd 16th
# of each beat), the "tss" between kicks. Always present; only the timbre varies.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    # 909-style open hat
    _cfg('open_hat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 420, 'envelope': {'attack': 0.001, 'decay': 0.22, 'release': 0.1},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 4800, 'octaves': 1.5},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Noise open hat — airier, more like a sampled hat
    _cfg('open_hat', 'hihat', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.12}},
         [_filt('highpass', 7500, 1)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Short, bright "tss"
    _cfg('open_hat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 550, 'envelope': {'attack': 0.001, 'decay': 0.12, 'release': 0.06},
          'harmonicity': 5.5, 'modulationIndex': 36, 'resonance': 6500, 'octaves': 1.6},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Long washy open hat in a small room
    _cfg('open_hat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.002, 'decay': 0.3, 'release': 0.15},
          'harmonicity': 4.6, 'modulationIndex': 28, 'resonance': 4200, 'octaves': 1.4},
         [_reverb(0.8, 0.15)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Noise open hat, darker and tighter
    _cfg('open_hat', 'hihat', -17, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 6000, 0.9)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# CLAPS / SNARES — beats 2 & 4. Optional and low-probability: plenty of techno
# runs on kick, rumble and hats alone, and an ever-present clap pulls it
# toward house.
# ---------------------------------------------------------------------------
_CLAPS = [
    # Dry clap
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.06}},
         [_filt('bandpass', 1500, 0.9), _reverb(0.6, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Roomy clap
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0, 'release': 0.08}},
         [_filt('bandpass', 1200, 0.7), _reverb(1.6, 0.35)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Tight snare
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.06}},
         [_filt('highpass', 400, 0.7)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Rim on the backbeat — a woody knock instead of a clap
    _cfg('clap', 'snare', -11, '16n', 'MembraneSynth',
         {'pitchDecay': 0.008, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 300, 0.7)],
         [_N,_N,_N,_N,'E4',_N,_N,_N,_N,_N,_N,_N,'E4',_N,_N,_N,
          _N,_N,_N,_N,'E4',_N,_N,_N,_N,_N,_N,_N,'E4',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# PERCUSSION — industrial and metallic hits, rimshots and toms on syncopated
# 16ths. Zero to two per track, each with its own id.
# ---------------------------------------------------------------------------
_PERCS = [
    # Rimshot syncopation
    _cfg('rimshot', 'perc', -14, '16n', 'MembraneSynth',
         {'pitchDecay': 0.006, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 400, 0.7)],
         [_N,_N,_N,'F#4',_N,_N,'F#4',_N,_N,_N,_N,_N,_N,_N,'F#4',_N,
          _N,_N,_N,'F#4',_N,_N,'F#4',_N,_N,_N,_N,'F#4',_N,_N,'F#4',_N]),
    # Industrial clang — distorted metal in a big room
    _cfg('clang', 'perc', -17, '16n', 'MetalSynth',
         {'frequency': 160, 'envelope': {'attack': 0.001, 'decay': 0.14, 'release': 0.06},
          'harmonicity': 3.1, 'modulationIndex': 18, 'resonance': 2200, 'octaves': 1.2},
         [_dist(0.5, 0.45), _reverb(1.4, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,_N,'C3',_N,_N]),
    # Dub metal ping thrown into a dotted-8th delay
    _cfg('ping', 'perc', -19, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.03},
          'harmonicity': 1.5, 'modulationIndex': 6, 'resonance': 3000, 'octaves': 0.5},
         [_delay('8n.', 0.45, 0.35)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N]),
    # Tribal tom loop
    _cfg('toms', 'perc', -14, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.08}},
         [_reverb(0.6, 0.15)],
         [_N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,'A2',_N,_N,'D3',_N,
          _N,_N,_N,_N,_N,_N,'D3',_N,_N,_N,_N,'A2',_N,_N,'F2',_N]),
    # Distorted noise bursts — the industrial "chk"
    _cfg('noise_hit', 'perc', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [_dist(0.8, 0.6), _filt('bandpass', 2500, 2)],
         [_N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,_N,_N,
          _N,_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,'C3',_N,_N]),
]

# ---------------------------------------------------------------------------
# STABS — the hypnotic element: a one- or two-note stab repeated unchanged, or
# a dub chord (Basic Channel style) dissolving into delay. Chords are written
# root-first so key coherence reads the root correctly.
# ---------------------------------------------------------------------------
_STABS = [
    # One-note hypnotic stab, filter slowly opening and closing
    _cfg('stab', 'stab', -16, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_filt('lowpass', 1400, 4), _delay('8n.', 0.4, 0.3), _reverb(1.8, 0.25)],
         [_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,
          _N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 700, 2600, 'tri')]),
    # Two-note FM stab bouncing in a ping-pong delay
    _cfg('stab', 'stab', -17, '16n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 8,
          'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.06},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.05}},
         [_filt('lowpass', 3000, 1.5), _pingpong('8n', 0.35, 0.3)],
         [_N,_N,'A3',_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,'A3',_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,_N]),
    # Dub chord — minor 7th on the offbeat, swallowed by delay
    _cfg('dub_chord', 'stab', -19, '16n', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0, 'release': 0.2}},
         [_filt('lowpass', 900, 1.5), _delay('8n.', 0.55, 0.45), _reverb(3.0, 0.35)],
         [_N,_N,_N,_N,_N,_N,'A3,C4,E4,G4',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'A3,C4,E4,G4',_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 500, 1800, 'tri')]),
    # Suspended dub chord stabbing twice per bar, ping-pong for width
    _cfg('dub_chord', 'stab', -20, '16n', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.004, 'decay': 0.3, 'sustain': 0, 'release': 0.25}},
         [_filt('lowpass', 1100, 1.2), _pingpong('4n.', 0.45, 0.4), _reverb(2.5, 0.3)],
         [_N,_N,'A3,D4,E4,G4',_N,_N,_N,_N,_N,_N,_N,'A3,D4,E4,G4',_N,_N,_N,_N,_N,
          _N,_N,'A3,D4,E4,G4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    # Metallic AM stab at the end of each bar
    _cfg('stab', 'stab', -17, '16n', 'AMSynth',
         {'harmonicity': 1.5,
          'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0, 'release': 0.1},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.1}},
         [_filt('bandpass', 1200, 1.5), _delay('8n', 0.35, 0.25)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'A3',_N]),
]

# ---------------------------------------------------------------------------
# PADS — a dark drone under everything, slowly filtered. Occasional; techno
# is a rhythm genre and the drone only sets the room.
# ---------------------------------------------------------------------------
_PADS = [
    _cfg('pad', 'pad', -24, '1m', 'Synth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 20},
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.8, 'release': 1.5}},
         [_filt('lowpass', 600, 1), _reverb(6.0, 0.6)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 300, 1200, 'tri')]),
    _cfg('pad', 'pad', -26, '1m', 'PolySynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.7, 'release': 1.2}},
         [_filt('lowpass', 800, 1), _chorus(0.6, 4, 0.5, 0.4), _reverb(5.0, 0.55)],
         ['A2,E3,C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A2,E3,C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -22, '1m', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 2,
          'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.8, 'release': 1.5},
          'modulationEnvelope': {'attack': 1.5, 'decay': 0.5, 'sustain': 0.6, 'release': 1.0}},
         [_filt('lowpass', 900, 1.5), _reverb(6.0, 0.6)],
         ['A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A2',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 400, 1500, 'tri')]),
]

# ---------------------------------------------------------------------------
# FILLS — sparse accents gated by loop_modulo so they fire every N loops only.
# Each loop = 2 bars, so loop_modulo=8 fires once every 16 bars (one "phrase").
# ---------------------------------------------------------------------------
_FILLS = [
    # Snare roll on the last beat of bar 2, every 16 bars
    _cfg('fill_roll', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [_reverb(0.5, 0.35)],
         [_N]*28 + ['C2', 'C2', 'C2', 'C2'],
         loop_modulo=8, loop_modulo_remainder=7),
    # Reverse-cymbal style swell, every 8 bars
    _cfg('fill_swell', 'perc', -16, '1n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 1.5, 'decay': 0.1, 'sustain': 0.9, 'release': 0.2}},
         [_reverb(2.0, 0.5), _filt('highpass', 1500, 1)],
         ['C3'] + [_N]*31,
         loop_modulo=4, loop_modulo_remainder=3),
    # Tom-style descending hit on the last quarter, every 16 bars
    _cfg('fill_tom', 'perc', -10, '8n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.4}},
         [_reverb(0.8, 0.35)],
         [_N]*24 + ['G1', _N, 'E1', _N, 'C1', _N, 'A0', _N],
         loop_modulo=8, loop_modulo_remainder=7),
]


class TechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.TECHNO
    BPM_RANGE = (130, 138)
    LEVEL_DB = -2.5
    KEY_ROLES = ('bass', 'hihat')
    SIDECHAIN_DEPTH = 0.8
    SIDECHAIN_RELEASE = 0.5

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        # The rumble is the sound of current techno; the offbeat and syncopated lines are the
        # older but equally canonical alternatives, so both families are drawn equally often.
        bass = copy.deepcopy(cls._pick(_RUMBLES if random.random() < 0.5 else _BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))

        _clear_kick_steps(bass, kick)
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        if bass['id'] == 'rumble':
            bass['pattern']['velocities'] = _vel_rumble(bass['pattern']['steps'])
        else:
            bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        open_hat['pattern']['velocities'] = _vel(open_hat['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)

        layers = [kick, bass, hihat, open_hat]

        clap = cls._maybe(_CLAPS, 0.35)
        if clap:
            clap = copy.deepcopy(clap)
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        for perc in random.sample(_PERCS, random.choice([0, 1, 1, 2])):
            perc = copy.deepcopy(perc)
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.25, ghost_prob=0.1)
            layers.append(perc)

        stab = cls._maybe(_STABS, 0.6)
        if stab:
            stab = copy.deepcopy(stab)
            stab['pattern']['velocities'] = _vel(stab['pattern']['steps'], accent_prob=0.25, ghost_prob=0.0)
            # Let the groove establish before the hypnotic element arrives
            if random.random() < 0.5:
                stab['entry_loop'] = random.choice([2, 4])
            layers.append(stab)

        pad = cls._maybe(_PADS, 0.25)
        if pad:
            layers.append(copy.deepcopy(pad))

        # Occasional phrase fill (snare roll / swell / tom run) — gated by loop_modulo,
        # so it only fires once every N loops instead of every bar.
        fill = cls._maybe(_FILLS, 0.5)
        if fill:
            layers.append(copy.deepcopy(fill))

        root_pc = cls._apply_key_coherence(layers)
        _tune_kick(kick, root_pc, _KICK_LOWEST_MIDI)
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _auto, _pingpong,
    _transpose_layer_to_root, _vel, _vel_groove, _vel_kick, _vel_snare, _four, _phrase, _roll,
)

# ---------------------------------------------------------------------------
# KICKS — hi-tech kicks are ticks: a near-instant pitch drop that is mostly
# click, done within a 32nd so the 190 BPM roll has room. No base saturation
# for this genre; at most a touch of drive on one variant.
# ---------------------------------------------------------------------------
_KICKS = [
    # Tick — barely any body, all attack
    _cfg('kick', 'kick', 1, '32n', 'MembraneSynth',
         {'pitchDecay': 0.01, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.03}},
         [], _four('A1')),
    # Snap — higher tuning, even shorter
    _cfg('kick', 'kick', 1, '32n', 'MembraneSynth',
         {'pitchDecay': 0.008, 'octaves': 7,
          'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.02}},
         [], _four('B1')),
    # Thump — a little more low end for the darker hi-tech tracks
    _cfg('kick', 'kick', 1, '32n', 'MembraneSynth',
         {'pitchDecay': 0.014, 'octaves': 5,
          'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.03}},
         [], _four('G#1')),
    # Driven tick — a light drive to sharpen the click
    _cfg('kick', 'kick', 1, '32n', 'MembraneSynth',
         {'pitchDecay': 0.01, 'octaves': 6,
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.025}},
         [_dist(0.2, 0.25)], _four('A#1')),
    # Laser tick — the widest sweep, a zap-like transient
    _cfg('kick', 'kick', 1, '32n', 'MembraneSynth',
         {'pitchDecay': 0.012, 'octaves': 8,
          'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.025}},
         [_filt('lowpass', 6000, 0.7)], _four('C2')),
]

# ---------------------------------------------------------------------------
# BASSES — rolling K-B-B-B like all psy, but every note is a 40-60 ms spike: a
# bright resonant filter snap per note and a cutoff swept across the loop.
# The roll is the constant; notes move by octave flicks and semitones.
# Written on A1; key coherence moves the root within a tritone.
# ---------------------------------------------------------------------------
_ZAP_SAW = {
    'oscillator': {'type': 'sawtooth'},
    'filter': {'type': 'lowpass', 'Q': 8, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.015},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.015,
                       'baseFrequency': 300, 'octaves': 3.5},
}
_ZAP_SQUARE = {
    'oscillator': {'type': 'square'},
    'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
    'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.015},
    'filterEnvelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.015,
                       'baseFrequency': 260, 'octaves': 4},
}
# FM at unison ratio: each note opens with a bright metallic bite that collapses within 25 ms
_FM_SNAP = {
    'harmonicity': 1, 'modulationIndex': 16,
    'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.015},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.025, 'sustain': 0, 'release': 0.01},
}
_FM_BITE = {
    'harmonicity': 2, 'modulationIndex': 10,
    'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0, 'release': 0.015},
    'modulationEnvelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01},
}

_BASSES = [
    # Root roll with an octave pop closing each bar
    _cfg('bass', 'bass', -6, '32n', 'MonoSynth', _ZAP_SAW,
         [_dist(0.25, 0.3), _filt('lowpass', 2000, 4)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1', 'A1 A1 A2',
               'A1 A1 A1', 'A1 A1 A1', 'A1 A1 A1', 'A1 C2 A2'),
         automation=[_auto('effect:1:frequency', 900, 5000, 'tri')]),
    # Octave rattle — every middle 16th an octave up, the whole line bright and jumpy
    _cfg('bass', 'bass', -7, '32n', 'FMSynth', _FM_SNAP,
         [_filt('lowpass', 2500, 3)],
         _roll('A1 A2 A1', 'A1 A2 A1', 'A1 A2 A1', 'A1 A2 A1',
               'A1 A2 A1', 'A1 A2 A1', 'C2 C3 C2', 'Bb1 Bb2 Bb1'),
         automation=[_auto('effect:0:frequency', 1200, 6000, 'ramp')]),
    # Semitone flick — the last 16th of each beat bends a half-step up
    _cfg('bass', 'bass', -6, '32n', 'MonoSynth', _ZAP_SQUARE,
         [_dist(0.3, 0.3), _filt('lowpass', 1800, 5)],
         _roll('A1 A1 Bb1', 'A1 A1 A1', 'A1 A1 Bb1', 'A1 A1 A1',
               'A1 A1 Bb1', 'A1 A1 A1', 'A1 A1 Bb1', 'C2 Bb1 A1'),
         automation=[_auto('effect:1:frequency', 800, 4500, 'tri')]),
    # Stepping roots — whole beats shift to the b2, b3 and the major seventh below
    _cfg('bass', 'bass', -6, '32n', 'MonoSynth', _ZAP_SAW,
         [_dist(0.2, 0.25), _filt('lowpass', 2200, 4)],
         _roll('A1 A1 A1', 'A1 A1 A1', 'Bb1 Bb1 Bb1', 'A1 A1 A1',
               'A1 A1 A1', 'A1 A1 A1', 'C2 C2 C2', 'G#1 G#1 G#1'),
         automation=[_auto('effect:1:frequency', 1000, 5500, 'tri')]),
    # Fifth skip — the middle 16th leaps to the fifth, a bouncing machine figure
    _cfg('bass', 'bass', -7, '32n', 'FMSynth', _FM_BITE,
         [_filt('lowpass', 2400, 4)],
         _roll('A1 E2 A1', 'A1 A1 A1', 'A1 E2 A1', 'A1 A1 A1',
               'A1 E2 A1', 'A1 A1 A1', 'A1 Eb2 A1', 'A1 A1 A2'),
         automation=[_auto('effect:0:frequency', 1000, 5000, 'tri')]),
    # Minor-third pop — the last 16th lifts to the third, darker turn in bar 2
    _cfg('bass', 'bass', -6, '32n', 'MonoSynth', _ZAP_SQUARE,
         [_dist(0.25, 0.3), _filt('lowpass', 1900, 5)],
         _roll('A1 A1 C2', 'A1 A1 A1', 'A1 A1 C2', 'A1 A1 A1',
               'A1 A1 C2', 'A1 A1 A1', 'Bb1 Bb1 Bb1', 'A1 A1 Bb1'),
         automation=[_auto('effect:1:frequency', 900, 4800, 'ramp')]),
]

# ---------------------------------------------------------------------------
# GLITCH FX — the sound of hi-tech: 32nd-note bursts of zaps, blips and
# stutters dropped into a few spots across the two bars (mostly the back half
# of beats and the bar ends), silent in between. 64 steps at 32n. Pitched ones
# are written around A and moved onto the track root after key coherence.
# ---------------------------------------------------------------------------
_GLITCH_FX = [
    # Zap bursts — FM at high modulation index, a ping-pong throwing them side to side
    _cfg('zap_burst', 'perc', -17, '32n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 60,
          'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.01},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.012, 'sustain': 0, 'release': 0.01}},
         [_pingpong('16n', 0.3, 0.25)],
         _phrase(64, (12, 'A5 A5 A5 A5'), (29, 'A5 - A5 E6'), (44, 'A5 A5 A5 A5'),
                 (56, 'E6 D6 C6 A5 A5 A5 A5 A5')),
         subdivision='32n'),
    # Blip runs — square arpeggios shooting up and down an octave
    _cfg('blip_run', 'perc', -19, '32n', 'Synth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.025, 'sustain': 0, 'release': 0.01}},
         [_filt('lowpass', 6000, 1), _pingpong('8n', 0.35, 0.3)],
         _phrase(64, (4, 'A5 C6 E6 A6'), (36, 'A6 E6 C6 A5'), (58, 'A5 A6 A5 A6 A5 A6')),
         subdivision='32n'),
    # Stutter — one FM note machine-gunned, then silence
    _cfg('stutter', 'perc', -18, '32n', 'FMSynth',
         {'harmonicity': 2, 'modulationIndex': 22,
          'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_dist(0.3, 0.3), _pingpong('16n', 0.25, 0.2)],
         _phrase(64, (20, 'A4 A4 A4 A4 A4 A4'), (52, 'A4 A4 A4 A4 C5 C5 A4 A4')),
         subdivision='32n'),
    # Laser — a gliding saw that swoops between octaves inside each burst
    _cfg('laser', 'perc', -20, '32n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'portamento': 0.015,
          'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.01}},
         [_filt('lowpass', 5000, 2), _delay('16n', 0.25, 0.2)],
         _phrase(64, (6, 'A6 A4'), (22, 'A6 A5 A4'), (38, 'A4 A6'), (54, 'A6 E6 A5 E5 A4 - A4 A4')),
         subdivision='32n'),
    # Digital chatter — dry inharmonic metal ticks in clipped clusters
    _cfg('chatter', 'perc', -19, '32n', 'MetalSynth',
         {'frequency': 1600, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.005},
          'harmonicity': 4.1, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.0},
         [_pingpong('16n', 0.4, 0.3)],
         _phrase(64, (14, 'C4 C4'), (28, 'C4 C4 C4 C4'), (46, 'C4 - C4 C4'), (60, 'C4 C4 C4 C4')),
         subdivision='32n'),
    # Zip — a falling FM cascade at the end of bar 1, a rising answer at the loop end
    _cfg('zip', 'perc', -18, '32n', 'FMSynth',
         {'harmonicity': 5.01, 'modulationIndex': 35,
          'envelope': {'attack': 0.001, 'decay': 0.03, 'sustain': 0, 'release': 0.01},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_pingpong('8n', 0.3, 0.25)],
         _phrase(64, (24, 'A6 G6 E6 D6 C6 A5 G5 E5'), (44, 'A5 A5'), (60, 'A5 C6 E6 A6')),
         subdivision='32n'),
    # Bit bleeps — lone sine pips scattered off the grid, left to bounce in a long ping-pong
    _cfg('bit_bleeps', 'perc', -20, '32n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_pingpong('8n.', 0.4, 0.35)],
         _phrase(64, (3, 'A6'), (13, 'E6'), (19, 'A6'), (30, 'A6 A6'), (43, 'C7'), (50, 'A6'),
                 (61, 'E6 A6')),
         subdivision='32n'),
]

# ---------------------------------------------------------------------------
# HI-HATS — fast closed 16ths, bright and short. _vel_groove shapes accents.
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -14, '32n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008},
          'harmonicity': 9.0, 'modulationIndex': 60, 'resonance': 7500, 'octaves': 2.0},
         [], ['C4'] * 32),
    _cfg('hihat', 'hihat', -14, '32n', 'MetalSynth',
         {'frequency': 1100, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.006},
          'harmonicity': 11, 'modulationIndex': 70, 'resonance': 10000, 'octaves': 2.4},
         [], ['C4'] * 32),
    # 16ths with the kick's slot left open — the hat ticks only between kicks
    _cfg('hihat', 'hihat', -14, '32n', 'MetalSynth',
         {'frequency': 950, 'envelope': {'attack': 0.001, 'decay': 0.013, 'release': 0.007},
          'harmonicity': 9.5, 'modulationIndex': 62, 'resonance': 9000, 'octaves': 2.3},
         [], [_N,'C4','C4','C4'] * 8),
    # Noise ticks — sharp high-passed hiss
    _cfg('hihat', 'hihat', -15, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.012, 'sustain': 0, 'release': 0.006}},
         [_filt('highpass', 8000, 0.8)], ['C4'] * 32),
    # 16ths with a skipped tick before every other beat — a stumbling machine
    _cfg('hihat', 'hihat', -14, '32n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.009},
          'harmonicity': 11, 'modulationIndex': 72, 'resonance': 10000, 'octaves': 2.5},
         [],
         ['C4','C4','C4','C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4','C4','C4',_N,
          'C4','C4','C4','C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4','C4',_N,'C4']),
    # Bright metal 16ths with light drive
    _cfg('hihat', 'hihat', -15, '32n', 'MetalSynth',
         {'frequency': 1300, 'envelope': {'attack': 0.001, 'decay': 0.011, 'release': 0.006},
          'harmonicity': 12, 'modulationIndex': 80, 'resonance': 12000, 'octaves': 2.8},
         [_dist(0.3, 0.3)], ['C4'] * 32),
]

# ---------------------------------------------------------------------------
# OPEN HATS — the off-beat "tss" on the and of every beat, over the 16ths.
# ---------------------------------------------------------------------------
_OPEN_HATS = [
    _cfg('open_hat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.07, 'release': 0.03},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 7000, 'octaves': 1.5},
         [], [_N,_N,'C4',_N] * 8),
    _cfg('open_hat', 'hihat', -16, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 6000, 0.8)], [_N,_N,'C4',_N] * 8),
    _cfg('open_hat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.09, 'release': 0.04},
          'harmonicity': 4.5, 'modulationIndex': 28, 'resonance': 8000, 'octaves': 1.6},
         [_reverb(0.8, 0.15)], [_N,_N,'C4',_N] * 8),
]

# ---------------------------------------------------------------------------
# SNARES — optional crisp backbeat, short enough to stay out of the glitches.
# ---------------------------------------------------------------------------
_SNARES = [
    _cfg('snare', 'snare', -13, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.03}},
         [_filt('highpass', 1800, 0.8)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('snare', 'snare', -14, '32n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 2200, 1), _reverb(0.6, 0.15)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,'C2']),
]

# ---------------------------------------------------------------------------
# LEADS — optional and sparse: a few high notes floating over the machinery,
# never a full melody (that would turn it into full-on).
# ---------------------------------------------------------------------------
_LEADS = [
    # FM bell — high, glassy, ping-ponged
    _cfg('bell', 'lead', -19, '16n', 'FMSynth',
         {'harmonicity': 3.5, 'modulationIndex': 8,
          'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.2},
          'modulationEnvelope': {'attack': 0.001, 'decay': 0.15, 'sustain': 0, 'release': 0.1}},
         [_pingpong('8n.', 0.35, 0.3), _reverb(1.8, 0.3)],
         [_N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,'E6',_N,_N,_N,_N,_N,
          _N,_N,'A5',_N,_N,_N,_N,_N,_N,_N,_N,_N,'C6',_N,'A5',_N]),
    # Pluck arp fragments — three-note saw plucks, delayed
    _cfg('pluck_arp', 'lead', -20, '32n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_filt('lowpass', 3500, 2), _delay('8n.', 0.3, 0.25)],
         [_N,_N,_N,_N,_N,_N,'A5','C6','E6',_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,'A5','C6','E6',_N,_N,_N,_N,_N,'A5',_N]),
    # Squeal — high resonant saw stabs with a fast filter snap
    _cfg('squeal', 'lead', -21, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'filter': {'type': 'lowpass', 'Q': 10, 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05,
                             'baseFrequency': 800, 'octaves': 3}},
         [_pingpong('16n', 0.3, 0.25)],
         [_N,_N,_N,'A6',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'Bb6',_N,
          _N,_N,_N,'A6',_N,_N,_N,_N,_N,_N,_N,'A6',_N,_N,_N,_N]),
    # Siren — a square gliding between root and fifth
    _cfg('siren', 'lead', -22, '8n', 'Synth',
         {'oscillator': {'type': 'square'}, 'portamento': 0.08,
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.2, 'release': 0.1}},
         [_filt('lowpass', 3000, 2), _delay('8n', 0.3, 0.2)],
         ['A5',_N,_N,_N,_N,_N,'E6',_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A5',_N,_N,_N,_N,_N,'F6',_N,_N,_N,_N,_N,'A5',_N,_N,_N],
         entry_loop=2),
    # High acid — a square line opening under a filter sweep
    _cfg('acid_high', 'lead', -21, '32n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'filter': {'type': 'lowpass', 'Q': 8, 'rolloff': -24},
          'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.03},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0, 'release': 0.03,
                             'baseFrequency': 600, 'octaves': 3}},
         [_filt('lowpass', 2000, 4), _pingpong('16n', 0.25, 0.2)],
         [_N,_N,'A5','A5',_N,_N,_N,_N,_N,_N,'C6','A5',_N,_N,_N,_N,
          _N,_N,'A5','A5',_N,_N,_N,_N,_N,_N,'E6','D6',_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 800, 6000, 'tri')]),
]

# ---------------------------------------------------------------------------
# RISERS — optional noise sweeps marking every fourth loop.
# ---------------------------------------------------------------------------
_RISERS = [
    _cfg('riser', 'pad', -20, '1m', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 1.2, 'decay': 0.1, 'sustain': 0.9, 'release': 0.1}},
         [_filt('highpass', 300, 2), _reverb(2.0, 0.4)],
         [_N] * 16 + ['C3'] + [_N] * 15,
         automation=[_auto('effect:0:frequency', 300, 9000, 'ramp')],
         loop_modulo=4, loop_modulo_remainder=3),
    _cfg('downlifter', 'pad', -21, '2n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.01, 'decay': 0.8, 'sustain': 0.3, 'release': 0.5}},
         [_filt('bandpass', 6000, 4), _reverb(2.5, 0.45)],
         ['C3'] + [_N] * 31,
         automation=[_auto('effect:0:frequency', 6000, 200, 'ramp')],
         loop_modulo=4, loop_modulo_remainder=0),
]


class HightekTrackGenerator(BaseTrackGenerator):
    """Hi-tech psytrance: a ticking kick, a needle-short rolling bass, and glitch FX as the signature."""
    GENRE = GenreType.HIGHTEK
    BPM_RANGE = (180, 195)
    LEVEL_DB = 0.0
    KEY_ROLES = ('perc', 'bass')
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.12

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        open_hat = copy.deepcopy(cls._pick(_OPEN_HATS))
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        # No ghost notes: a quiet 16th reads as a hole in the roll
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.3, ghost_prob=0.0)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        open_hat['pattern']['velocities'] = _vel(open_hat['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
        layers = [kick, bass, hihat, open_hat]

        # Half the tracks trade two different glitch layers loop by loop, so the FX never repeat
        # exactly — the restlessness is part of the genre.
        if random.random() < 0.5:
            glitches = [copy.deepcopy(fx) for fx in random.sample(_GLITCH_FX, 2)]
            for remainder, fx in enumerate(glitches):
                fx['loop_modulo'] = 2
                fx['loop_modulo_remainder'] = remainder
        else:
            glitches = [copy.deepcopy(cls._pick(_GLITCH_FX))]
        for fx in glitches:
            fx['pattern']['velocities'] = _vel(fx['pattern']['steps'], accent_prob=0.3, ghost_prob=0.15)
        layers.extend(glitches)

        lead = cls._maybe(_LEADS, 0.4)
        if lead is not None:
            lead = copy.deepcopy(lead)
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.2, ghost_prob=0.0)
            layers.append(lead)

        snare = cls._maybe(_SNARES, 0.45)
        if snare is not None:
            snare = copy.deepcopy(snare)
            snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
            layers.append(snare)

        riser = cls._maybe(_RISERS, 0.35)
        if riser is not None:
            layers.append(copy.deepcopy(riser))

        root = cls._apply_key_coherence(layers)
        # The glitches are percussion by role (so the reveal points at them) but most are pitched;
        # key coherence skips percussion, so move them onto the root here.
        for fx in glitches:
            _transpose_layer_to_root(fx, root)
        return layers

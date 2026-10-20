import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _auto, _pingpong,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

# ---------------------------------------------------------------------------
# KICKS — deep, round, strictly four-on-the-floor. The rolling bass fills every
# gap between quarters, so there is no room for pickups here.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.38, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Longer, softer body
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Warm saturation, a little more weight in the mids
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.34, 'sustain': 0.01, 'release': 0.85}},
         [_dist(0.18, 0.25)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Tighter — for the faster end of the tempo range
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.75}},
         [],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,
          'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N]),
    # Big and boomy with a hint of room
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.0}},
         [_reverb(0.5, 0.06)],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,
          'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.36, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# CLAPS — on 2 and 4, light and roomy. They mark the backbeat without pulling
# focus from the arp and pads.
# ---------------------------------------------------------------------------
_CLAPS = [
    _cfg('clap', 'snare', -13, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.06}},
         [_reverb(1.2, 0.28)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -14, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.08}},
         [_filt('highpass', 800, 0.7), _reverb(1.6, 0.32)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Snappier, drier
    _cfg('clap', 'snare', -13, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.05}},
         [_filt('highpass', 1100, 0.7), _reverb(0.9, 0.22)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HATS — offbeat-led and restrained; the arp already supplies the 16th motion.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Offbeat open hat
    _cfg('hihat', 'hihat', -13, '8n', 'MetalSynth',
         {'frequency': 600, 'envelope': {'attack': 0.001, 'decay': 0.09, 'release': 0.05}, 'harmonicity': 6.5, 'modulationIndex': 40, 'resonance': 6000, 'octaves': 1.7},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Quiet closed 16ths, velocity-shaped
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.007}, 'harmonicity': 8.5, 'modulationIndex': 50, 'resonance': 7000, 'octaves': 2.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Offbeats with a 16th pickup into each bar
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.03}, 'harmonicity': 7.2, 'modulationIndex': 44, 'resonance': 6500, 'octaves': 1.8},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4','C4',
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4','C4']),
    # Closed 8ths
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 820, 'envelope': {'attack': 0.001, 'decay': 0.016, 'release': 0.008}, 'harmonicity': 9.0, 'modulationIndex': 52, 'resonance': 7500, 'octaves': 2.1},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # Airy noise hat on the offbeats
    _cfg('hihat', 'hihat', -16, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_filt('highpass', 8000, 0.7)],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# PERCUSSION — optional ear candy: a wide shaker or a tom figure that leads
# back into the loop.
# ---------------------------------------------------------------------------
_PERCS = [
    _cfg('shaker', 'perc', -20, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.003, 'decay': 0.03, 'sustain': 0, 'release': 0.015}},
         [_filt('highpass', 6000, 0.7)],
         [_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',
          _N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4'],
         pan=0.35),
    # Low tom roll at the end of bar 2
    _cfg('tom', 'perc', -14, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 2.5, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.1}},
         [_reverb(2.0, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'G2',_N,'E2','D2',_N],
         pan=-0.2),
    # Rim with a long dotted echo
    _cfg('rim', 'perc', -17, '32n', 'MembraneSynth',
         {'pitchDecay': 0.005, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0, 'release': 0.03}},
         [_delay('8n.', 0.4, 0.3)],
         [_N,_N,_N,_N,_N,_N,_N,'E5',_N,_N,_N,_N,_N,_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'E5',_N,_N,_N,_N],
         pan=0.25),
]

# ---------------------------------------------------------------------------
# HARMONY — bass, arp and pad are written together per 2-bar progression, all
# in A minor, and a track always takes all three from the same progression so
# they agree in bar 2 as well as bar 1. Key coherence then moves the whole
# track to its root; A is the most common note in every line below, so all
# three layers shift by the same amount.
#
# BASS: the rolling offbeat line — the 2nd-3rd-4th (or 3rd-4th) 16ths of each
# beat, never on the kick, so kick and bass interlock into one pulse. Warm
# saw through a lowpass whose cutoff drifts slowly over the loop.
#
# ARP: 16th-note pluck outlining each bar's chord, pushed back with a dotted
# delay and reverb — the Afterlife hook.
#
# PAD: wide minor chords that swell and pump against the sidechain.
# ---------------------------------------------------------------------------
_BASS_WARM = {'oscillator': {'type': 'sawtooth'},
              'envelope': {'attack': 0.004, 'decay': 0.14, 'sustain': 0.45, 'release': 0.07},
              'filter': {'type': 'lowpass', 'Q': 1.2, 'rolloff': -24},
              'filterEnvelope': {'attack': 0.004, 'decay': 0.11, 'sustain': 0.25, 'release': 0.08, 'baseFrequency': 110, 'octaves': 2.2}}
_BASS_FAT = {'oscillator': {'type': 'fatsawtooth', 'count': 2, 'spread': 14},
             'envelope': {'attack': 0.005, 'decay': 0.16, 'sustain': 0.5, 'release': 0.08},
             'filter': {'type': 'lowpass', 'Q': 1, 'rolloff': -24},
             'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.3, 'release': 0.08, 'baseFrequency': 100, 'octaves': 2.0}}
_BASS_PLUCKY = {'oscillator': {'type': 'sawtooth'},
                'envelope': {'attack': 0.003, 'decay': 0.1, 'sustain': 0.3, 'release': 0.05},
                'filter': {'type': 'lowpass', 'Q': 2, 'rolloff': -24},
                'filterEnvelope': {'attack': 0.003, 'decay': 0.07, 'sustain': 0.15, 'release': 0.05, 'baseFrequency': 120, 'octaves': 2.8}}

_ARP_SAW = {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.002, 'decay': 0.16, 'sustain': 0.0, 'release': 0.12}}
_ARP_SOFT = {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.0, 'release': 0.15}}
_ARP_BELL = {'harmonicity': 2, 'modulationIndex': 7,
             'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.0, 'release': 0.2},
             'modulationEnvelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.0, 'release': 0.1}}
_ARP_SQUARE = {'oscillator': {'type': 'square'}, 'envelope': {'attack': 0.002, 'decay': 0.14, 'sustain': 0.0, 'release': 0.1},
               'filter': {'type': 'lowpass', 'Q': 3, 'rolloff': -24},
               'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.0, 'release': 0.1, 'baseFrequency': 500, 'octaves': 3.0}}

_PAD_SUPERSAW = {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 28},
                 'envelope': {'attack': 0.6, 'decay': 0.6, 'sustain': 0.8, 'release': 2.2}}
_PAD_WARM = {'oscillator': {'type': 'fattriangle', 'count': 3, 'spread': 22},
             'envelope': {'attack': 0.4, 'decay': 0.5, 'sustain': 0.85, 'release': 1.8}}


def _pad_fx() -> list[dict]:
    """Lowpass first so automation can open it; chorus for width; a long, wet reverb for the scale."""
    return [_filt('lowpass', 1500, 0.8), _chorus(0.35, 3.5, 0.6, 0.35), _reverb(6.0, 0.55, 0.03)]


# i–VI: Am → F. The most-used move in the genre — hopeful and sad at once.
_BASSES_I_VI = [
    # Full gallop: 2nd, 3rd and 4th 16ths of every beat
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth', _BASS_WARM,
         [_filt('lowpass', 500, 1.2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'F1','F1','F1',_N,'F1','F1','F1',_N,'F1','F1','F1',_N,'F1','F1','F1'],
         automation=[_auto('effect:0:frequency', 260, 1100, 'tri')]),
    # Gallop with an octave flick on the last 16th
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _BASS_FAT,
         [_filt('lowpass', 450, 1.2)],
         [_N,'A1','A1','A2',_N,'A1','A1','A2',_N,'A1','A1','A2',_N,'A1','A1','A2',
          _N,'F1','F1','F2',_N,'F1','F1','F2',_N,'F1','F1','F2',_N,'F1','F1','F2'],
         automation=[_auto('effect:0:frequency', 240, 1300, 'tri')]),
    # 3rd and 4th 16ths only — more air, more bounce
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth', _BASS_PLUCKY,
         [_filt('lowpass', 550, 1.4)],
         [_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',
          _N,_N,'F1','F1',_N,_N,'F1','F1',_N,_N,'F1','F1',_N,_N,'F1','F1'],
         automation=[_auto('effect:0:frequency', 300, 1400, 'tri')]),
]

_ARPS_I_VI = [
    # Up and down through the chord
    _cfg('arp', 'lead', -13, '16n', 'Synth', _ARP_SAW,
         [_filt('lowpass', 2000, 2), _delay('8n.', 0.38, 0.28), _reverb(4.5, 0.4, 0.02)],
         ['A3','C4','E4','A4','C5','A4','E4','C4','A3','C4','E4','A4','C5','A4','E4','C4',
          'A3','C4','F4','A4','C5','A4','F4','C4','A3','C4','F4','A4','C5','A4','F4','C4'],
         automation=[_auto('effect:0:frequency', 800, 4200, 'tri')]),
    # Skipping bell figure — the rests let the ping-pong echo fill in
    _cfg('arp', 'lead', -14, '16n', 'FMSynth', _ARP_BELL,
         [_filt('lowpass', 3000, 1), _pingpong('8n.', 0.35, 0.3), _reverb(5.0, 0.45, 0.02)],
         ['A3',_N,'A4','E4',_N,'A4','A3',_N,'A4','E4',_N,'C5','A4',_N,'E4','C4',
          'A3',_N,'A4','F4',_N,'A4','A3',_N,'A4','F4',_N,'C5','A4',_N,'F4','C4'],
         automation=[_auto('effect:0:frequency', 1200, 5000, 'tri')]),
    # Octave-hopping square pluck
    _cfg('arp', 'lead', -15, '16n', 'MonoSynth', _ARP_SQUARE,
         [_delay('8n.', 0.4, 0.3), _reverb(4.0, 0.42, 0.02)],
         ['A3','A4','E4','A4','A3','A4','E4','A4','C4','C5','E4','C5','C4','C5','A4','E4',
          'A3','A4','F4','A4','A3','A4','F4','A4','C4','C5','F4','C5','C4','C5','A4','F4']),
]

_PADS_I_VI = [
    # Held supersaw chords, one per bar
    _cfg('pad', 'pad', -17, '1m', 'PolySynth', _PAD_SUPERSAW, _pad_fx(),
         ['A3,C4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'F3,A3,C4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 700, 2600, 'tri')]),
    # Open voicing re-struck every half bar
    _cfg('pad', 'pad', -17, '2n', 'PolySynth', _PAD_WARM, _pad_fx(),
         ['A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,'A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,
          'F3,C4,A4',_N,_N,_N,_N,_N,_N,_N,'F3,C4,A4',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 900, 3000, 'tri')]),
]

# i–VII: Am → G. Darker and more driving; the step down never resolves upward.
_BASSES_I_VII = [
    # Full gallop, the last beat climbs back to A for the turnaround
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth', _BASS_WARM,
         [_filt('lowpass', 480, 1.2)],
         [_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',_N,'A1','A1','A1',
          _N,'G1','G1','G1',_N,'G1','G1','G1',_N,'G1','G1','G1',_N,'G1','A1','A1'],
         automation=[_auto('effect:0:frequency', 250, 1200, 'tri')]),
    # 3rd and 4th 16ths only
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _BASS_FAT,
         [_filt('lowpass', 520, 1.2)],
         [_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',_N,_N,'A1','A1',
          _N,_N,'G1','G1',_N,_N,'G1','G1',_N,_N,'G1','G1',_N,_N,'G1','G1'],
         automation=[_auto('effect:0:frequency', 280, 1350, 'tri')]),
]

_ARPS_I_VII = [
    # Pulsing root-fifth figure; G carries an added A to keep the line connected
    _cfg('arp', 'lead', -13, '16n', 'Synth', _ARP_SAW,
         [_filt('lowpass', 1800, 2), _delay('8n.', 0.4, 0.3), _reverb(4.5, 0.42, 0.02)],
         ['A3','E4','A4','E4','A3','E4','A4','E4','A3','E4','C5','E4','A3','E4','A4','C5',
          'B3','G4','A4','G4','B3','G4','A4','G4','B3','G4','B4','G4','B3','G4','A4','B4'],
         automation=[_auto('effect:0:frequency', 700, 4000, 'tri')]),
    # Climbing bell
    _cfg('arp', 'lead', -14, '16n', 'FMSynth', _ARP_BELL,
         [_filt('lowpass', 2800, 1), _delay('8n.', 0.36, 0.28), _reverb(5.0, 0.45, 0.02)],
         ['A3','C4','E4','A4','C4','E4','A4','C5','E4','A4','C5','E5','A4','C5','A4','E4',
          'B3','D4','G4','A4','D4','G4','A4','B4','G4','A4','B4','D5','A4','B4','A4','G4'],
         automation=[_auto('effect:0:frequency', 1100, 4800, 'tri')]),
    # Soft triplet-feel gallop (three notes and a rest)
    _cfg('arp', 'lead', -12, '16n', 'Synth', _ARP_SOFT,
         [_filt('lowpass', 2400, 1.5), _pingpong('8n.', 0.38, 0.3), _reverb(5.5, 0.45, 0.02)],
         ['A3','E4','A4',_N,'A3','E4','C5',_N,'A3','E4','A4',_N,'C4','E4','C5',_N,
          'B3','G4','A4',_N,'B3','G4','B4',_N,'B3','G4','A4',_N,'D4','G4','B4',_N],
         automation=[_auto('effect:0:frequency', 900, 3800, 'tri')]),
]

_PADS_I_VII = [
    _cfg('pad', 'pad', -17, '1m', 'PolySynth', _PAD_SUPERSAW, _pad_fx(),
         ['A3,C4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G3,B3,D4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 700, 2400, 'tri')]),
    _cfg('pad', 'pad', -17, '2n', 'PolySynth', _PAD_WARM, _pad_fx(),
         ['A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,'A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,
          'G3,D4,B4',_N,_N,_N,_N,_N,_N,_N,'G3,D4,B4',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 900, 2800, 'tri')]),
]

# i–iv: Am → Dm. The most melancholic of the three; the arp holds A on top
# through both chords.
_BASSES_I_IV = [
    # Alternating full and half gallops
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth', _BASS_WARM,
         [_filt('lowpass', 500, 1.2)],
         [_N,'A1','A1','A1',_N,_N,'A1','A1',_N,'A1','A1','A1',_N,_N,'A1','A1',
          _N,'D2','D2','D2',_N,_N,'D2','D2',_N,'D2','D2','D2',_N,_N,'D2','D2'],
         automation=[_auto('effect:0:frequency', 260, 1150, 'tri')]),
    # Bouncing octave in the middle of each beat
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth', _BASS_PLUCKY,
         [_filt('lowpass', 520, 1.4)],
         [_N,'A1','A2','A1',_N,'A1','A2','A1',_N,'A1','A2','A1',_N,'A1','A2','A1',
          _N,'D2','D3','D2',_N,'D2','D3','D2',_N,'D2','D3','D2',_N,'D2','D3','D2'],
         automation=[_auto('effect:0:frequency', 300, 1300, 'tri')]),
]

_ARPS_I_IV = [
    # Gallop with a rest on each beat's last 16th
    _cfg('arp', 'lead', -13, '16n', 'Synth', _ARP_SAW,
         [_filt('lowpass', 1900, 2), _delay('8n.', 0.4, 0.3), _reverb(4.5, 0.42, 0.02)],
         ['A3','E4','A4',_N,'A3','E4','C5',_N,'A3','E4','A4',_N,'C4','E4','C5',_N,
          'A3','F4','A4',_N,'A3','F4','D5',_N,'A3','F4','A4',_N,'D4','F4','D5',_N],
         automation=[_auto('effect:0:frequency', 800, 4200, 'tri')]),
    # Climbing bell
    _cfg('arp', 'lead', -14, '16n', 'FMSynth', _ARP_BELL,
         [_filt('lowpass', 2800, 1), _pingpong('8n.', 0.35, 0.28), _reverb(5.0, 0.45, 0.02)],
         ['A3','C4','E4','A4','C4','E4','A4','C5','E4','A4','C5','E5','A4','C5','A4','E4',
          'A3','D4','F4','A4','D4','F4','A4','D5','F4','A4','D5','F5','A4','D5','A4','F4'],
         automation=[_auto('effect:0:frequency', 1100, 4800, 'tri')]),
]

_PADS_I_IV = [
    _cfg('pad', 'pad', -17, '1m', 'PolySynth', _PAD_SUPERSAW, _pad_fx(),
         ['A3,C4,E4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'A3,D4,F4',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 700, 2500, 'tri')]),
    _cfg('pad', 'pad', -17, '2n', 'PolySynth', _PAD_WARM, _pad_fx(),
         ['A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,'A3,E4,C5',_N,_N,_N,_N,_N,_N,_N,
          'D3,A3,F4',_N,_N,_N,_N,_N,_N,_N,'D3,A3,F4',_N,_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:0:frequency', 900, 2900, 'tri')]),
]

_PROGRESSIONS = [
    (_BASSES_I_VI, _ARPS_I_VI, _PADS_I_VI),
    (_BASSES_I_VII, _ARPS_I_VII, _PADS_I_VII),
    (_BASSES_I_IV, _ARPS_I_IV, _PADS_I_IV),
]


class MelodicTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.MELODIC_TECHNO
    BPM_RANGE = (120, 126)
    LEVEL_DB = -2.1
    KEY_ROLES = ('lead', 'pad')
    # Full pump with a slow recovery: the pads and bass visibly breathe around every kick.
    SIDECHAIN_DEPTH = 1.0
    SIDECHAIN_RELEASE = 0.75

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        basses, arps, pads = random.choice(_PROGRESSIONS)
        kick = copy.deepcopy(cls._pick(_KICKS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(basses))
        arp = copy.deepcopy(cls._pick(arps))
        pad = copy.deepcopy(cls._pick(pads))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.15, ghost_prob=0.05)
        arp['pattern']['velocities'] = _vel(arp['pattern']['steps'], accent_prob=0.2, ghost_prob=0.06)
        pad['pattern']['velocities'] = _vel(pad['pattern']['steps'], accent_prob=0.0, ghost_prob=0.0)

        # Usually the arp is there from the first bar; sometimes the pad and bass set the mood first.
        arp['entry_loop'] = random.choice([0, 0, 0, 1])

        layers = [kick, hihat, bass, arp, pad]

        if random.random() < 0.8:
            clap = copy.deepcopy(cls._pick(_CLAPS))
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        if random.random() < 0.4:
            perc = copy.deepcopy(cls._pick(_PERCS))
            perc['pattern']['velocities'] = _vel(perc['pattern']['steps'], accent_prob=0.2, ghost_prob=0.15)
            perc['dropout_prob'] = random.choice([0.0, 0.2, 0.3])
            layers.append(perc)

        cls._apply_key_coherence(layers)
        return layers

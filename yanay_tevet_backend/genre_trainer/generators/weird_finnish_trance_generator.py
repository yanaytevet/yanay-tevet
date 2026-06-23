import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay, _dist, _filt, _chorus, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

# ---------------------------------------------------------------------------
# KICKS — classic trance 4/4, slightly soft (not as hard as techno).
# Long tail and subtle drive — let the leads be the focal point.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.12, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.6, 'sustain': 0.01, 'release': 1.8}},
         [_reverb(1.0, 0.2)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.55, 'sustain': 0.01, 'release': 1.6}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.3}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.11, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.65, 'sustain': 0.01, 'release': 2.0}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# CLAPS — backbeat on 2 & 4.
# ---------------------------------------------------------------------------
_CLAPS = [
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0, 'release': 0.05}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -7, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
    _cfg('clap', 'snare', -8, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.8, 0.3)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — classic trance offbeat openhat ("tss-tss-tss-tss")
# ---------------------------------------------------------------------------
_HIHATS = [
    # Offbeat open-hat — defining trance sound
    _cfg('hihat', 'hihat', -13, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.12, 'release': 0.08},
          'harmonicity': 2.5, 'modulationIndex': 12, 'resonance': 7000, 'octaves': 1.0},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Closed 16ths
    _cfg('hihat', 'hihat', -14, '16n', 'MetalSynth',
         {'frequency': 950, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.008},
          'harmonicity': 9.0, 'modulationIndex': 55, 'resonance': 8500, 'octaves': 2.2},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 8th-note open
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.1, 'release': 0.06},
          'harmonicity': 3.0, 'modulationIndex': 15, 'resonance': 7500, 'octaves': 1.2},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
]

# ---------------------------------------------------------------------------
# BASSES — trance sub bass on each kick (mirrors the kick), with the
# classic offbeat triangle/sine motif. Sometimes a rolling 16th line.
# ---------------------------------------------------------------------------
_BASSES = [
    # B minor — sub mirror of kick with melodic descent
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.7, 'release': 0.25},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.6, 'release': 0.25,
                             'baseFrequency': 60, 'octaves': 1.2}},
         [_filt('lowpass', 250, 1.5)],
         ['B1',_N,_N,_N,'B1',_N,_N,_N,'B1',_N,_N,_N,'A1',_N,_N,_N,
          'B1',_N,_N,_N,'B1',_N,_N,_N,'G1',_N,_N,_N,'F#1',_N,_N,_N]),
    # E minor offbeat — sub on kick, offbeat saw
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.12, 'sustain': 0.4, 'release': 0.1},
          'filterEnvelope': {'attack': 0.003, 'decay': 0.08, 'sustain': 0.2, 'release': 0.1,
                             'baseFrequency': 80, 'octaves': 3.5}},
         [_filt('lowpass', 600, 4), _dist(0.3, 0.3)],
         ['E1',_N,'E1',_N,'E1',_N,'E1',_N,'E1',_N,'E1',_N,'E1',_N,'E1',_N,
          'E1',_N,'E1',_N,'E1',_N,'E1',_N,'D1',_N,'D1',_N,'E1',_N,'B0',_N],
         automation=[_auto('effect:0:frequency', 350, 1800, 'tri')]),
    # D minor with chord-tone movement
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.72, 'release': 0.28},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.62, 'release': 0.28,
                             'baseFrequency': 55, 'octaves': 1.0}},
         [_filt('lowpass', 220, 1.5)],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'F1',_N,_N,_N,
          'A1',_N,_N,_N,'A1',_N,_N,_N,'G1',_N,_N,_N,'F1',_N,_N,_N]),
    # F# minor — emotional with octave answer
    _cfg('bass', 'bass', -4, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.7, 'release': 0.28},
          'filterEnvelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.62, 'release': 0.28,
                             'baseFrequency': 58, 'octaves': 1.1}},
         [_filt('lowpass', 240, 1.5)],
         ['F#1',_N,_N,_N,'F#1',_N,_N,_N,'F#1',_N,_N,_N,'F#1',_N,_N,_N,
          'D1',_N,_N,_N,'D1',_N,_N,_N,'E1',_N,_N,_N,'F#1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# LEADS — lush, melodic, the heart of trance. Long delay tails + reverb
# create the wide stereo trance sound. Filter automation on lead 1 & 5
# adds the classic supersaw "opening up" effect.
# ---------------------------------------------------------------------------
_LEADS = [
    # B minor melodic — climbing motif
    _cfg('lead', 'lead', -8, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(2.5, 0.5, 0.03), _delay('8n.', 0.4, 0.3), _filt('lowpass', 2500, 1.5)],
         ['B4',_N,'D5',_N,'F#5',_N,'G5',_N,'F#5',_N,'E5',_N,'D5',_N,'B4',_N,
          'B4',_N,'C#5',_N,'D5',_N,'F#5',_N,'A5',_N,'G5',_N,'F#5','E5',_N,_N],
         automation=[_auto('effect:2:frequency', 700, 5500, 'tri')]),
    # E minor climbing
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(3.0, 0.55, 0.04), _delay('8n.', 0.38, 0.28)],
         ['E5',_N,'G5',_N,'B5',_N,'E6',_N,'B5',_N,'G5',_N,'E5',_N,'D5',_N,
          'E5',_N,'G5',_N,'B5',_N,'D6',_N,'B5',_N,'G5',_N,'D5',_N,'B4',_N]),
    # D minor rising
    _cfg('lead', 'lead', -8, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.22, 'release': 0.5}},
         [_reverb(2.8, 0.52, 0.03), _delay('8n.', 0.42, 0.32)],
         ['D5',_N,'F#5',_N,'A5',_N,'D6',_N,'A5',_N,'F#5',_N,'D5',_N,'C#5',_N,
          'D5',_N,'F#5',_N,'A5',_N,'C#6',_N,'A5',_N,'F#5',_N,'E5',_N,'D5',_N]),
    # A minor high register
    _cfg('lead', 'lead', -7, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.008, 'decay': 0.3, 'sustain': 0.25, 'release': 0.55}},
         [_reverb(3.2, 0.58, 0.04), _delay('8n.', 0.45, 0.35)],
         ['A5',_N,'C#6',_N,'E6',_N,'A6',_N,'E6',_N,'C#6',_N,'A5',_N,'G5',_N,
          'A5',_N,'C#6',_N,'E6',_N,'G6',_N,'E6',_N,'C#6',_N,'B5',_N,'A5',_N]),
    # F# minor square — Finnish-rave brashness
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.2, 'release': 0.4}},
         [_reverb(2.2, 0.45, 0.02), _filt('lowpass', 4000, 2)],
         ['F#5',_N,'A5',_N,'D6',_N,'F#6',_N,'D6',_N,'A5',_N,'F#5',_N,'E5',_N,
          'F#5',_N,'A5',_N,'C#6',_N,'F#6',_N,'E6',_N,'D6',_N,'C#6',_N,'B5',_N],
         automation=[_auto('effect:1:frequency', 1500, 6000, 'tri')]),
    # B minor breakdown — slow descending
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0.22, 'release': 0.45}},
         [_reverb(3.5, 0.6, 0.05), _delay('4n', 0.35, 0.2)],
         ['B5',_N,_N,'D6','F#6',_N,'B5',_N,'A5',_N,_N,'E5','G5',_N,'F#5',_N,
          'B5',_N,_N,'D6','G6',_N,'F#6','E6','D6',_N,'C#6',_N,'B5',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# PADS — lush emotional foundation
# ---------------------------------------------------------------------------
_PADS = [
    _cfg('pad', 'pad', -14, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.1, 'decay': 0.5, 'sustain': 0.6, 'release': 1.0}},
         [_reverb(4.0, 0.7)],
         ['B3',_N,_N,_N,_N,_N,_N,_N,'D4',_N,_N,_N,_N,_N,_N,_N,
          'G3',_N,_N,_N,_N,_N,_N,_N,'F#3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -16, '16n', 'AMSynth',
         {'harmonicity': 0.5,
          'envelope': {'attack': 0.2, 'decay': 0.5, 'sustain': 0.7, 'release': 1.2},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.8, 'release': 1.0}},
         [_reverb(5.0, 0.8)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,'B3',_N,_N,_N,_N,_N,_N,_N,
          'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -15, '16n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.3, 'decay': 0.6, 'sustain': 0.75, 'release': 1.5}},
         [_reverb(5.5, 0.85)],
         ['D3',_N,_N,_N,_N,_N,_N,_N,'F#3',_N,_N,_N,_N,_N,_N,_N,
          'A3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# ARPS — high-register 16th arpeggios in the trance keys
# ---------------------------------------------------------------------------
_ARPS = [
    # B minor triad arp
    _cfg('arp', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.002, 'decay': 0.08, 'sustain': 0.1, 'release': 0.15}},
         [_reverb(2.0, 0.45), _delay('16n', 0.25, 0.15)],
         ['B4','D5','F#5','B5','D5','F#5','B4','D5','B4','D5','F#5','B5','F#5','D5','B4','D5',
          'B4','D5','G5','B5','D5','G5','B4','D5','A4','E5','A5','E5','A4','E5','A5','E5']),
    # E minor arp
    _cfg('arp', 'lead', -14, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.1, 'sustain': 0.12, 'release': 0.18}},
         [_reverb(2.5, 0.5), _delay('8n', 0.2, 0.12)],
         ['E5','G5','B5','E5','G5','B5','E5','G5','E5','A5','C#6','E5','A5','C#6','E5','A5',
          'D5','F#5','A5','D5','F#5','A5','D5','F#5','E5','G#5','B5','E5','G#5','B5','E5','G#5']),
    # F# minor arp
    _cfg('arp', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.09, 'sustain': 0.08, 'release': 0.12}},
         [_reverb(1.8, 0.4), _delay('16n', 0.3, 0.18)],
         ['F#5','A5','D6','F#5','A5','D6','F#5','A5','E5','G#5','B5','E5','G#5','B5','E5','G#5',
          'B4','D#5','F#5','B4','D#5','F#5','B4','D#5','A4','C#5','E5','A4','C#5','E5','A4','C#5']),
]


class WeirdFinnishTranceTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.WEIRD_FINNISH_TRANCE
    BPM_RANGE = (138, 143)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        clap = copy.deepcopy(cls._pick(_CLAPS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        lead = copy.deepcopy(cls._pick(_LEADS))
        pad = copy.deepcopy(cls._pick(_PADS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
        lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.25, ghost_prob=0.05)

        # Lead may enter after intro — classic trance arrangement
        if random.random() < 0.5:
            lead['entry_loop'] = random.choice([2, 4])

        layers = [kick, clap, hihat, bass, pad, lead]

        # Arp adds the high-register sparkle
        if random.random() < 0.5:
            arp = copy.deepcopy(cls._pick(_ARPS))
            arp['pattern']['velocities'] = _vel(arp['pattern']['steps'], accent_prob=0.18, ghost_prob=0.1)
            arp['entry_loop'] = random.choice([0, 2])
            layers.append(arp)

        cls._apply_key_coherence(layers)
        return layers

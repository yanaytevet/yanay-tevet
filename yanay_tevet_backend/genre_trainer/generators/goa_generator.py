import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _reverb, _delay, _dist, _chorus, _filt, _auto,
    _vel, _vel_groove, _vel_kick,
)

# ---------------------------------------------------------------------------
# KICKS — softer than dark psy / hard psy, more "bouncy" classic '90s feel.
# Slight reverb on a couple, never very distorted — that's the Goa signature.
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', -3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 1.4}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.7}},
         [_reverb(1.0, 0.14)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.46, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.6}},
         [_reverb(1.5, 0.18)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Anticipation hit before bar-2 beat 1 — classic Goa transition
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.062, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.44, 'sustain': 0.01, 'release': 1.4}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — classic '90s metallic shimmer, sparser than full-on
# ---------------------------------------------------------------------------
_HIHATS = [
    # Offbeat 8ths
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 3.5, 'modulationIndex': 18, 'resonance': 7000, 'octaves': 1.0},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # On the "and" — classic disco-style
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.015},
          'harmonicity': 3.0, 'modulationIndex': 16, 'resonance': 6500, 'octaves': 1.0},
         [],
         [_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Full 16ths driving
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 3.2, 'modulationIndex': 17, 'resonance': 6000, 'octaves': 1.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Sparse breathing
    _cfg('hihat', 'hihat', -18, '16n', 'MetalSynth',
         {'frequency': 720, 'envelope': {'attack': 0.001, 'decay': 0.038, 'release': 0.018},
          'harmonicity': 3.0, 'modulationIndex': 16, 'resonance': 6200, 'octaves': 1.0},
         [],
         [_N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N,
          _N,_N,'C4',_N,'C4',_N,_N,_N,_N,_N,'C4',_N,_N,_N,'C4',_N]),
    # Open-hat feel — longer decay
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 680, 'envelope': {'attack': 0.001, 'decay': 0.06, 'release': 0.04},
          'harmonicity': 2.8, 'modulationIndex': 14, 'resonance': 5500, 'octaves': 0.9},
         [],
         [_N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N,
          _N,_N,'C4',_N,_N,'C4',_N,_N,_N,_N,'C4',_N,_N,'C4',_N,_N]),
]

# ---------------------------------------------------------------------------
# BASSES — Goa typically uses rolling acid 303-style bass with filter sweeps.
# Phrygian dominant scale gives the "Indian / Middle Eastern" colour.
# Bass plays mostly on offbeats but with more melodic movement than full-on.
# ---------------------------------------------------------------------------
_MONO_GOA = {
    'oscillator': {'type': 'sawtooth'},
    'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.0, 'release': 0.06},
    'filterEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.0, 'release': 0.06,
                       'baseFrequency': 150, 'octaves': 4.5},
}

_BASSES = [
    # D Phrygian dominant — exotic colour
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_dist(0.35, 0.4), _filt('lowpass', 600, 5)],
         [_N,_N,'D1',_N,'F1',_N,'D1',_N,_N,_N,'Eb1',_N,'A1',_N,'D1',_N,
          _N,_N,'D1',_N,'F1',_N,'C2',_N,_N,_N,'A1',_N,'G1',_N,'F1',_N],
         automation=[_auto('effect:1:frequency', 250, 2400, 'tri')]),
    # E Phrygian dominant
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_dist(0.32, 0.4), _filt('lowpass', 650, 5)],
         [_N,_N,'E1',_N,'G1',_N,'E1',_N,_N,_N,'F1',_N,'B1',_N,'E1',_N,
          _N,_N,'E1',_N,'G1',_N,'B1',_N,_N,_N,'D2',_N,'C2',_N,'B1',_N],
         automation=[_auto('effect:1:frequency', 280, 2600, 'tri')]),
    # A Phrygian dominant — exotic Indian scale
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_dist(0.36, 0.42), _filt('lowpass', 620, 5)],
         [_N,_N,'A1',_N,'C2',_N,'A1',_N,_N,_N,'Bb1',_N,'E2',_N,'A1',_N,
          _N,_N,'A1',_N,'C#2',_N,'E2',_N,_N,_N,'C2',_N,'Bb1',_N,'A1',_N],
         automation=[_auto('effect:1:frequency', 300, 2500, 'tri')]),
    # G Phrygian — minor with chromatic descent
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth', _MONO_GOA,
         [_dist(0.35, 0.4), _filt('lowpass', 580, 5)],
         [_N,_N,'G1',_N,'A1',_N,'G1',_N,_N,_N,'Ab1',_N,'D2',_N,'G1',_N,
          _N,_N,'G1',_N,'A1',_N,'C2',_N,_N,_N,'A1',_N,'G1',_N,'F1',_N]),
    # E Phrygian — alternating with octave jump
    _cfg('bass', 'bass', -8, '16n', 'MonoSynth', _MONO_GOA,
         [_reverb(0.6, 0.12), _filt('lowpass', 700, 4)],
         [_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E2',_N,_N,_N,'E1',_N,
          _N,_N,'E1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,'B1',_N],
         automation=[_auto('effect:1:frequency', 250, 2200, 'tri')]),
    # A Phrygian rolling melodic answer in bar 2
    _cfg('bass', 'bass', -7, '16n', 'MonoSynth', _MONO_GOA,
         [_dist(0.4, 0.42), _filt('lowpass', 600, 5)],
         [_N,_N,'A1',_N,'A1',_N,'A1',_N,_N,_N,'G1',_N,'A1',_N,'E1',_N,
          _N,_N,'A1',_N,'C2',_N,'D2',_N,_N,_N,'C2',_N,'Bb1',_N,'A1',_N]),
]

# ---------------------------------------------------------------------------
# LEADS — the heart of Goa: layered 16th-note acid lead lines in
# Phrygian/Phrygian-dominant. Long delay tails for the trance hypnosis.
# Filter automation on key effects creates evolving brightness.
# ---------------------------------------------------------------------------
_LEADS = [
    # D Phrygian dominant — exotic melodic phrase
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.2, 'release': 0.5}},
         [_reverb(3.0, 0.5, 0.05), _delay('8n', 0.4, 0.3), _filt('lowpass', 3000, 2)],
         ['D5',_N,'F5',_N,'A5',_N,'C6',_N,'A5',_N,'G5',_N,'F5',_N,'D5',_N,
          'D5',_N,'Eb5',_N,'F5',_N,'A5',_N,'C6',_N,'A5',_N,'G5',_N,'E5',_N],
         automation=[_auto('effect:2:frequency', 800, 6500, 'tri')]),
    # E Phrygian dominant — climbing
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(2.5, 0.55, 0.02), _delay('8n', 0.3, 0.25), _filt('lowpass', 2800, 2)],
         ['E5',_N,_N,'F5',_N,_N,'G5',_N,'F5',_N,_N,_N,'E5',_N,_N,_N,
          'D5',_N,_N,'E5',_N,_N,'G5',_N,'A5',_N,_N,_N,'B5',_N,'A5',_N],
         automation=[_auto('effect:2:frequency', 700, 5800, 'tri')]),
    # A Phrygian dominant — pinging arpeggio
    _cfg('lead', 'lead', -10, '16n', 'AMSynth',
         {'harmonicity': 1.0,
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.2, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.5, 'release': 0.5}},
         [_reverb(3.0, 0.6, 0.02), _delay('8n.', 0.3, 0.25)],
         ['A5',_N,_N,_N,'C#6',_N,'E6',_N,'D6',_N,'C#6',_N,'A5',_N,_N,_N,
          'A5',_N,_N,_N,'C#6',_N,'E6',_N,'F#6',_N,_N,_N,'E6',_N,'C#6',_N]),
    # G Phrygian dominant — descending answer
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.25, 'sustain': 0.18, 'release': 0.45}},
         [_reverb(3.0, 0.6, 0.02), _delay('8n.', 0.32, 0.22), _filt('lowpass', 2500, 2.5)],
         ['G5',_N,_N,'Ab5',_N,'Bb5',_N,_N,'C6',_N,'Bb5',_N,'Ab5',_N,_N,_N,
          'G5',_N,_N,'Ab5','C6',_N,'D6',_N,'C6','Bb5',_N,_N,'Ab5',_N,_N,_N],
         automation=[_auto('effect:2:frequency', 600, 5000, 'tri')]),
    # E Phrygian — high-energy 16th saw run
    _cfg('lead', 'lead', -9, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.22, 'release': 0.5}},
         [_reverb(4.0, 0.7, 0.04), _delay('8n.', 0.45, 0.35)],
         ['E5','G5','B5','E6','B5','G5','E5','D5','E5','G5','B5','D6','B5','G5','D5','C5',
          'E5','G5','B5','E6','G6','E6','B5','G5','A5','C6','E6','A6','E6','C6','A5','G5']),
    # A Phrygian — chromatic answer at top
    _cfg('lead', 'lead', -9, '16n', 'AMSynth',
         {'harmonicity': 1.0,
          'envelope': {'attack': 0.005, 'decay': 0.3, 'sustain': 0.25, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.5, 'decay': 0.2, 'sustain': 0.5, 'release': 0.5}},
         [_reverb(5.0, 0.72, 0.05), _delay('8n.', 0.5, 0.38)],
         ['A5','C6','E6','A6','E6','C6','A5','G5','A5','C6','E6','G6','E6','C6','G5','F5',
          'A5','C6','E6','A6','B6','A6','E6','C6','D6','F6','A6','D7','A6','F6','D6','C6']),
    # B Phrygian — uplifting melodic answer with FM colour
    _cfg('lead', 'lead', -10, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 6,
          'envelope': {'attack': 0.005, 'decay': 0.28, 'sustain': 0.2, 'release': 0.48},
          'modulationEnvelope': {'attack': 0.4, 'decay': 0.15, 'sustain': 0.4, 'release': 0.4}},
         [_reverb(3.5, 0.65, 0.03), _delay('8n', 0.35, 0.28)],
         ['B5',_N,'D6',_N,'E6',_N,'G6',_N,'E6',_N,'D6',_N,'B5',_N,'A5',_N,
          'B5',_N,'D6',_N,'E6',_N,'F#6',_N,'E6',_N,'D6','B5',_N,_N,'A5',_N]),
]

# ---------------------------------------------------------------------------
# ARPS — high-register triangle/sine arpeggios, hypnotic
# ---------------------------------------------------------------------------
_ARPS = [
    # D minor triplet-arp
    _cfg('arp', 'lead', -15, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0.1, 'release': 0.2}},
         [_reverb(2.5, 0.5), _delay('16n', 0.3, 0.2)],
         ['D6','F6','A6','D7','A6','F6','D6','C6','D6','F6','A6','C7','A6','F6','C6','Bb5',
          'D6','F6','A6','D7','F7','D7','A6','F6','E6','G6','B6','E7','B6','G6','E6','D6']),
    # E minor arp
    _cfg('arp', 'lead', -16, '16n', 'AMSynth',
         {'harmonicity': 0.5,
          'envelope': {'attack': 0.002, 'decay': 0.12, 'sustain': 0.08, 'release': 0.18},
          'modulationEnvelope': {'attack': 0.4, 'decay': 0.1, 'sustain': 0.4, 'release': 0.3}},
         [_reverb(3.0, 0.55), _delay('16n', 0.28, 0.22)],
         ['E6','G6','B6','E7','B6','G6','E6','D6','E6','G6','B6','D7','B6','G6','D6','C6',
          'E6','G6','B6','E7','G7','E7','B6','G6','A6','C7','E7','A7','E7','C7','A6','G6']),
    # A minor sparse — sine
    _cfg('arp', 'lead', -17, '16n', 'Synth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.003, 'decay': 0.2, 'sustain': 0.12, 'release': 0.25}},
         [_reverb(4.0, 0.6), _delay('8n', 0.4, 0.3)],
         ['A5',_N,'C6',_N,'E6',_N,'A6',_N,'E6',_N,'C6',_N,'A5',_N,'G5',_N,
          'B5',_N,'D6',_N,'G6',_N,'D6',_N,'B5',_N,'G5',_N,'F5',_N,'E5',_N]),
]

# ---------------------------------------------------------------------------
# PADS — long emotional pads, the Goa "cosmic" texture
# ---------------------------------------------------------------------------
_PADS = [
    _cfg('pad', 'pad', -18, '16n', 'AMSynth',
         {'harmonicity': 0.8,
          'envelope': {'attack': 0.6, 'decay': 0.5, 'sustain': 0.8, 'release': 2.5},
          'modulationEnvelope': {'attack': 0.7, 'decay': 0.3, 'sustain': 0.7, 'release': 2.0}},
         [_reverb(5.0, 0.8)],
         ['D3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'F3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
    _cfg('pad', 'pad', -20, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.8, 'decay': 0.5, 'sustain': 0.9, 'release': 3.0}},
         [_reverb(6.0, 0.85), _chorus(0.4, 4, 0.5, 0.3)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,
          'G3',_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N],
         entry_loop=2),
]


class GoaTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.GOA
    BPM_RANGE = (136, 142)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        lead = copy.deepcopy(cls._pick(_LEADS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.05)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.22, ghost_prob=0.06)

        layers = [kick, bass, hihat, lead]

        # Arp — layered acid lead is a Goa signature
        if random.random() < 0.55:
            arp = copy.deepcopy(cls._pick(_ARPS))
            arp['pattern']['velocities'] = _vel(arp['pattern']['steps'], accent_prob=0.18, ghost_prob=0.1)
            arp['entry_loop'] = random.choice([0, 2])
            layers.append(arp)

        # Pad — slower harmonic glue for emotional content
        if random.random() < 0.45:
            layers.append(copy.deepcopy(cls._pick(_PADS)))

        cls._apply_key_coherence(layers)
        return layers

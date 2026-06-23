import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.85}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.3, 'sustain': 0.01, 'release': 0.9}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.05, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.0}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.75}},
         [_dist(0.25, 0.25)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.29, 'sustain': 0.01, 'release': 0.88}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.048, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.32, 'sustain': 0.01, 'release': 0.95}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_CLAPS = [
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.5, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -10, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.07}},
         [_reverb(0.7, 0.25)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    _cfg('clap', 'snare', -9, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_reverb(0.6, 0.22)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
]

_HIHATS = [
    _cfg('hihat', 'hihat', -9, '16n', 'MetalSynth',
         {'frequency': 700, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.008}, 'harmonicity': 8.0, 'modulationIndex': 48, 'resonance': 6500, 'octaves': 2.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.007}, 'harmonicity': 9.0, 'modulationIndex': 55, 'resonance': 7500, 'octaves': 2.2},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    _cfg('hihat', 'hihat', -9, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.016, 'release': 0.009}, 'harmonicity': 8.5, 'modulationIndex': 50, 'resonance': 7000, 'octaves': 2.1},
         [],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4']),
    _cfg('hihat', 'hihat', -10, '16n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.018, 'release': 0.01}, 'harmonicity': 7.5, 'modulationIndex': 44, 'resonance': 6000, 'octaves': 1.9},
         [],
         ['C4','C4','C4','C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4','C4','C4',_N,'C4','C4','C4','C4','C4','C4','C4',_N]),
]

_BASSES = [
    # Deep A minor sub
    _cfg('bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.015, 'decay': 0.28, 'sustain': 0.75, 'release': 0.35}, 'filterEnvelope': {'attack': 0.015, 'decay': 0.38, 'sustain': 0.7, 'release': 0.32, 'baseFrequency': 60, 'octaves': 1.2}},
         [],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'G0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'F0',_N,_N,_N,'G0',_N,_N,_N]),
    # Punchy E minor
    _cfg('bass', 'bass', -1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.005, 'decay': 0.18, 'sustain': 0.55, 'release': 0.25}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.3, 'release': 0.22, 'baseFrequency': 65, 'octaves': 2.5}},
         [_filt('lowpass', 500, 3)],
         ['E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N,'E1',_N,_N,_N]),
    # D moving bass
    _cfg('bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.012, 'decay': 0.24, 'sustain': 0.72, 'release': 0.32}, 'filterEnvelope': {'attack': 0.012, 'decay': 0.32, 'sustain': 0.68, 'release': 0.3, 'baseFrequency': 58, 'octaves': 1.1}},
         [],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'C1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N]),
    # G with slight drive
    _cfg('bass', 'bass', -1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.6, 'release': 0.28}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.15, 'sustain': 0.32, 'release': 0.25, 'baseFrequency': 62, 'octaves': 2.2}},
         [_filt('lowpass', 550, 3)],
         ['G0',_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,'F0',_N,_N,_N,'G0',_N,_N,_N,'A0',_N,_N,_N,'G0',_N,_N,_N]),
    # B minor deep rumble
    _cfg('bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.02, 'decay': 0.32, 'sustain': 0.78, 'release': 0.4}, 'filterEnvelope': {'attack': 0.02, 'decay': 0.42, 'sustain': 0.74, 'release': 0.38, 'baseFrequency': 55, 'octaves': 1.0}},
         [],
         ['B0',_N,_N,_N,'B0',_N,_N,_N,'A0',_N,_N,_N,'B0',_N,_N,_N,'B0',_N,_N,_N,'G0',_N,_N,_N,'A0',_N,_N,_N,'B0',_N,_N,_N]),
]

_PADS = [
    # Afterlife-style emotional pad
    _cfg('pad', 'pad', -8, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.3, 'decay': 0.5, 'sustain': 0.8, 'release': 1.5}, 'modulationEnvelope': {'attack': 0.6, 'decay': 0.3, 'sustain': 0.85, 'release': 1.2}},
         [_reverb(5.0, 0.82), _chorus(0.5, 3.5, 0.7, 0.4)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'E4',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -9, '16n', 'AMSynth',
         {'harmonicity': 0.4, 'envelope': {'attack': 0.4, 'decay': 0.4, 'sustain': 0.78, 'release': 1.6}, 'modulationEnvelope': {'attack': 0.7, 'decay': 0.25, 'sustain': 0.8, 'release': 1.4}},
         [_reverb(5.5, 0.85)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,'B3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -8, '16n', 'FMSynth',
         {'harmonicity': 0.3, 'modulationIndex': 4, 'envelope': {'attack': 0.35, 'decay': 0.45, 'sustain': 0.82, 'release': 1.7}, 'modulationEnvelope': {'attack': 0.5, 'decay': 0.3, 'sustain': 0.82, 'release': 1.5}},
         [_reverb(6.0, 0.88)],
         ['D3',_N,_N,_N,_N,_N,_N,_N,'F3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -9, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.45, 'decay': 0.5, 'sustain': 0.8, 'release': 1.8}},
         [_reverb(5.8, 0.86), _chorus(0.4, 4.0, 0.6, 0.35)],
         ['G3',_N,_N,_N,_N,_N,_N,_N,'B3',_N,_N,_N,_N,_N,_N,_N,'D4',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N]),
]

_LEADS = [
    # A minor reaching upward — filter sweep adds the Afterlife shimmer
    _cfg('lead', 'lead', -10, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.4, 'release': 0.8}},
         [_reverb(3.5, 0.7, 0.04), _delay('8n.', 0.35, 0.25), _filt('lowpass', 3000, 1.5)],
         ['A4',_N,_N,'C5','E5',_N,'D5',_N,'C5',_N,_N,'A4','G4',_N,_N,'E4',
          'A4',_N,_N,'C5','E5',_N,'G5','F5','E5',_N,'D5',_N,'C5',_N,_N,_N],
         automation=[_auto('effect:2:frequency', 800, 5500, 'tri')]),
    # E minor melodic — climbing motif
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.28, 'sustain': 0.38, 'release': 0.75}},
         [_reverb(4.0, 0.72, 0.05), _delay('8n.', 0.32, 0.22), _filt('lowpass', 2800, 1.5)],
         ['E5',_N,_N,'G5','B5',_N,'A5',_N,'G5',_N,_N,'E5','D5',_N,_N,'B4',
          'E5',_N,_N,'G5','B5',_N,'D6','C6','B5',_N,'A5',_N,'G5',_N,_N,_N],
         automation=[_auto('effect:2:frequency', 700, 5000, 'tri')]),
    # D minor FM with emotional curve
    _cfg('lead', 'lead', -10, '16n', 'FMSynth',
         {'harmonicity': 1.5, 'modulationIndex': 5, 'envelope': {'attack': 0.012, 'decay': 0.32, 'sustain': 0.42, 'release': 0.82}, 'modulationEnvelope': {'attack': 0.015, 'decay': 0.25, 'sustain': 0.28, 'release': 0.75}},
         [_reverb(3.8, 0.72, 0.04), _delay('4n', 0.28, 0.18)],
         ['D5',_N,_N,'F5','A5',_N,'G5',_N,'F5',_N,_N,'D5','C5',_N,_N,'A4',
          'D5',_N,_N,'F5','A5',_N,'C6','A5','G5',_N,'F5',_N,'E5',_N,_N,_N]),
    # G major (relative) — uplifting
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.26, 'sustain': 0.35, 'release': 0.7}},
         [_reverb(4.2, 0.74, 0.05), _delay('8n.', 0.38, 0.28)],
         ['B4',_N,_N,'D5','G5',_N,'F#5',_N,'E5',_N,_N,'C5','B4',_N,_N,'G4',
          'B4',_N,_N,'D5','G5',_N,'A5','G5','F#5',_N,'E5',_N,'D5',_N,_N,_N]),
]


class MelodicTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.MELODIC_TECHNO
    BPM_RANGE = (130, 138)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        pad = copy.deepcopy(cls._pick(_PADS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.18, ghost_prob=0.05)

        # Pad enters first — sets the emotional tone before the rest comes in
        layers = [kick, hihat, bass, pad]

        if random.random() < 0.6:
            clap = copy.deepcopy(cls._pick(_CLAPS))
            clap['pattern']['velocities'] = _vel_snare(clap['pattern']['steps'])
            layers.append(clap)

        if random.random() < 0.6:
            lead = copy.deepcopy(cls._pick(_LEADS))
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.22, ghost_prob=0.05)
            # Lead enters after the groove establishes — Afterlife arrangement
            lead['entry_loop'] = random.choice([2, 4])
            layers.append(lead)

        cls._apply_key_coherence(layers)
        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _chorus, _auto,
    _vel, _vel_groove, _vel_kick,
)

# ---------------------------------------------------------------------------
# KICKS — deep sub kicks with long tail (midtempo psy bass anchors on the kick).
# ---------------------------------------------------------------------------
_KICKS = [
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.5}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.3}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    # Half-time alternation — bass becomes the rhythmic driver
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.35, 'sustain': 0.01, 'release': 1.2}},
         [],
         ['C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,'C1',_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 12, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 1.2}},
         [_dist(0.5, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    # Slow half-time feel — every other quarter
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.7, 'sustain': 0.01, 'release': 2.0}},
         [],
         ['C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N,
          'C1',_N,_N,_N,_N,_N,_N,_N,'C1',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.08, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.4}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.09, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.52, 'sustain': 0.01, 'release': 1.5}},
         [_reverb(0.8, 0.12)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,
          'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# ---------------------------------------------------------------------------
# HI-HATS — dark, low-frequency metallic shimmer (not bright like full-on).
# Sparse to leave space for the heavy bass.
# ---------------------------------------------------------------------------
_HIHATS = [
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.01},
          'harmonicity': 6.0, 'modulationIndex': 40, 'resonance': 3000, 'octaves': 2.0},
         [],
         [_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,
          _N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -15, '16n', 'MetalSynth',
         {'frequency': 300, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 5.0, 'modulationIndex': 35, 'resonance': 2800, 'octaves': 1.8},
         [],
         [_N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N,
          _N,_N,'C3',_N,_N,_N,_N,_N,_N,_N,'C3',_N,_N,'C3',_N,_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 320, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.01},
          'harmonicity': 7.0, 'modulationIndex': 45, 'resonance': 3500, 'octaves': 2.2},
         [],
         [_N,_N,'C3',_N,'C3',_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N,
          _N,_N,'C3',_N,'C3',_N,_N,'C3',_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 350, 'envelope': {'attack': 0.001, 'decay': 0.035, 'release': 0.015},
          'harmonicity': 4.5, 'modulationIndex': 30, 'resonance': 4000, 'octaves': 1.5},
         [],
         ['C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,
          'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N,'C3',_N]),
    _cfg('hihat', 'hihat', -18, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.015}},
         [],
         [_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,
          _N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N,_N,_N,'C3',_N]),
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 280, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.012},
          'harmonicity': 6.5, 'modulationIndex': 42, 'resonance': 2600, 'octaves': 2.0},
         [],
         [_N,_N,'C3','C3',_N,_N,'C3',_N,_N,_N,'C3','C3',_N,_N,'C3',_N,
          _N,_N,'C3','C3',_N,_N,'C3',_N,_N,_N,'C3','C3',_N,_N,'C3',_N]),
]

# ---------------------------------------------------------------------------
# BASSES — the main character. Heavy FM growls, dubby sub pulses, square
# squelches. Each has filter automation that sweeps to create movement.
# ---------------------------------------------------------------------------
_FM_GROWL = {
    'harmonicity': 0.5, 'modulationIndex': 20,
    'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.6, 'release': 0.2},
    'modulationEnvelope': {'attack': 0.005, 'decay': 0.08, 'sustain': 0.3, 'release': 0.2},
}

_BASSES = [
    # A minor rolling FM growl with delay echo
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.5, 'release': 0.2},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.3, 'release': 0.2,
                             'baseFrequency': 100, 'octaves': 5}},
         [_dist(0.6, 0.6), _delay('16n', 0.2, 0.1), _filt('lowpass', 800, 5)],
         ['A1','A1',_N,'C2','A1',_N,'G1','A1',_N,'C2','A1',_N,'G1',_N,'A1',_N,
          'A1','A1',_N,'C2','E2',_N,'D2','C2','A1',_N,'G1','A1','C2',_N,'A1',_N],
         automation=[_auto('effect:2:frequency', 400, 2800, 'tri')]),
    # Sustained sub-bass A — deep pad-like
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.03, 'decay': 0.4, 'sustain': 0.8, 'release': 0.4},
          'filterEnvelope': {'attack': 0.03, 'decay': 0.5, 'sustain': 0.7, 'release': 0.4,
                             'baseFrequency': 60, 'octaves': 1}},
         [],
         ['A0',_N,_N,_N,_N,_N,_N,_N,'G0',_N,_N,_N,_N,_N,_N,_N,
          'A0',_N,_N,_N,_N,_N,_N,_N,'E0',_N,_N,_N,_N,_N,_N,_N]),
    # AM minor growl with mod motion
    _cfg('bass', 'bass', -4, '16n', 'AMSynth',
         {'harmonicity': 0.5,
          'envelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.7, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.1, 'decay': 0.2, 'sustain': 0.8, 'release': 0.2}},
         [_dist(0.5, 0.5), _filt('lowpass', 800, 6)],
         ['A1',_N,'A1','C2','A1',_N,'G1','A1',_N,'A1',_N,'E1','D1','E1',_N,_N,
          'A1',_N,'A1','C2','E2',_N,'D2','C2','B1',_N,'A1',_N,'G1','A1',_N,_N],
         automation=[_auto('effect:1:frequency', 350, 2400, 'tri')]),
    # D minor sub pulse — half-time sustained
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'},
          'envelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.85, 'release': 0.3},
          'filterEnvelope': {'attack': 0.02, 'decay': 0.4, 'sustain': 0.8, 'release': 0.3,
                             'baseFrequency': 55, 'octaves': 1}},
         [],
         ['D1',_N,_N,_N,'F1',_N,_N,_N,'G1',_N,_N,_N,'A1',_N,_N,_N,
          'D1',_N,_N,_N,'F1',_N,_N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N]),
    # D minor heavy FM growl with reverb tail
    _cfg('bass', 'bass', -6, '16n', 'FMSynth', _FM_GROWL,
         [_dist(0.6, 0.6), _reverb(0.4, 0.15, 0.005), _filt('lowpass', 1000, 4)],
         ['D2',_N,'D2','F2','D2',_N,'C2','D2','F2','D2',_N,'C2','D2',_N,'A1','C2',
          'D2',_N,'D2','F2','A2','F2','D2','C2','A1','G1','F1',_N,'G1','A1',_N,_N],
         automation=[_auto('effect:2:frequency', 500, 3000, 'tri')]),
    # G minor melodic growl with chromatic neighbours
    _cfg('bass', 'bass', -5, '16n', 'FMSynth',
         {'harmonicity': 0.75, 'modulationIndex': 18,
          'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.65, 'release': 0.25},
          'modulationEnvelope': {'attack': 0.008, 'decay': 0.1, 'sustain': 0.4, 'release': 0.25}},
         [_dist(0.45, 0.45), _filt('lowpass', 1200, 4)],
         ['G2',_N,'G2','A2','G2','F2','G2',_N,'F2','G2',_N,'E2','D2',_N,'E2','F2',
          'G2',_N,'G2','A2','C3','A2','G2','F2','E2','D2','C2',_N,'D2','E2',_N,_N],
         automation=[_auto('effect:1:frequency', 450, 2800, 'tri')]),
    # E minor square squelch — 303-style
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'square'},
          'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0.4, 'release': 0.1},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.2, 'release': 0.1,
                             'baseFrequency': 80, 'octaves': 4}},
         [_dist(0.55, 0.55), _filt('lowpass', 900, 5)],
         ['E2','E2',_N,'G2','E2','D2','E2',_N,'G2','E2',_N,'D2','E2','G2',_N,_N,
          'E2','E2',_N,'G2','B2','G2','E2',_N,'D2','E2','G2',_N,'E2',_N,_N,'D2'],
         automation=[_auto('effect:1:frequency', 300, 2600, 'tri')]),
]

# ---------------------------------------------------------------------------
# LEADS — high-register melodic/atmospheric, optional, ~50% of tracks.
# Always reverb-heavy so they sit far back behind the bass.
# ---------------------------------------------------------------------------
_LEADS = [
    _cfg('lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 2.0, 'modulationIndex': 8,
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.4, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.2, 'release': 0.3}},
         [_reverb(1.5, 0.4), _delay('16n', 0.3, 0.2)],
         ['A3',_N,'C4',_N,'E4',_N,'G4',_N,'A4',_N,'G4',_N,'E4',_N,'C4',_N,
          'A3',_N,'B3',_N,'D4',_N,'F4',_N,'A4',_N,'G4',_N,'F4','E4',_N,_N]),
    _cfg('lead', 'lead', -13, '16n', 'AMSynth',
         {'harmonicity': 1.5,
          'envelope': {'attack': 0.008, 'decay': 0.2, 'sustain': 0.35, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.02, 'decay': 0.15, 'sustain': 0.3, 'release': 0.35}},
         [_reverb(2.0, 0.5, 0.01), _dist(0.4, 0.4)],
         ['D4',_N,_N,'F4','D4',_N,'A3','D4',_N,'F4','D4',_N,'C4',_N,'A3',_N,
          'D4',_N,_N,'F4','A4',_N,'G4','F4','E4',_N,'D4',_N,'C4','D4',_N,_N]),
    _cfg('lead', 'lead', -11, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'},
          'envelope': {'attack': 0.003, 'decay': 0.18, 'sustain': 0.35, 'release': 0.4}},
         [_reverb(2.5, 0.55, 0.02), _filt('lowpass', 3000, 2)],
         ['E4','E4',_N,'G4','A4',_N,'G4','E4','D4','E4',_N,'G4','A4',_N,_N,'G4',
          'E4',_N,'E4','G4','B4','G4','E4',_N,'D4','E4','G4',_N,'A4',_N,_N,_N],
         automation=[_auto('effect:1:frequency', 1000, 5000, 'tri')]),
    _cfg('lead', 'lead', -12, '16n', 'FMSynth',
         {'harmonicity': 3.0, 'modulationIndex': 12,
          'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.3, 'release': 0.5},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.12, 'sustain': 0.15, 'release': 0.4}},
         [_reverb(3.0, 0.6, 0.03), _delay('8n', 0.25, 0.15)],
         ['A4',_N,_N,'E4','G4',_N,'D4',_N,'A3','C4',_N,'E4',_N,'A4',_N,_N,
          'A4','G4',_N,'E4','A4',_N,'C5',_N,'A4','G4',_N,'E4',_N,'D4',_N,_N]),
    _cfg('lead', 'lead', -13, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.4, 'release': 0.5}},
         [_reverb(3.5, 0.65, 0.04), _delay('8n.', 0.3, 0.2)],
         ['C5',_N,'A4',_N,'G4',_N,'E4',_N,'D4',_N,'C4',_N,'A3',_N,'G3',_N,
          'C5',_N,'B4',_N,'A4',_N,'G4',_N,'E4',_N,'D4',_N,'C4',_N,'A3',_N]),
]


class PsyBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSY_BASS
    BPM_RANGE = (138, 143)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        bass = copy.deepcopy(cls._pick(_BASSES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.22, ghost_prob=0.08)
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])

        layers = [kick, bass, hihat]

        # Lead — atmospheric overlay in ~half of tracks
        if random.random() < 0.5:
            lead = copy.deepcopy(cls._pick(_LEADS))
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.2, ghost_prob=0.08)
            lead['entry_loop'] = random.choice([0, 2, 4])
            layers.append(lead)

        return layers

import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt, _auto,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

_KICKS = [
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 14, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.7}},
         [_dist(0.6, 0.55)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.022, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.01, 'release': 0.6}},
         [_dist(0.75, 0.65)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.65}},
         [_dist(0.7, 0.6)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.024, 'octaves': 15, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.8}},
         [_dist(0.65, 0.58)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.018, 'octaves': 17, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0.01, 'release': 0.55}},
         [_dist(0.8, 0.7)],
         ['C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 3, '8n', 'MembraneSynth',
         {'pitchDecay': 0.02, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.19, 'sustain': 0.01, 'release': 0.62}},
         [_dist(0.72, 0.62)],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.026, 'octaves': 13, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.55, 0.5)],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

# Snare patterns — main hits at steps 4,12,20,28 (beats 2&4).
# Some include ghost-hit positions; _vel_snare makes those quiet at generation time.
_SNARES = [
    # Standard 2/4
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_dist(0.5, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Ghost hit on "and of 2" (step 6) and "and of 2" of bar 2 (step 22)
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.11, 'sustain': 0, 'release': 0.07}},
         [_dist(0.52, 0.5)],
         [_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Ghost anticipation before beat 4 of bar 2 (step 27)
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.08}},
         [_dist(0.5, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,'C2','C2',_N,_N,_N]),
    # Drop beat 2 of bar 2 for tension — only 3 hits per cycle
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.13, 'sustain': 0, 'release': 0.09}},
         [_dist(0.5, 0.5)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,
          _N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Pink noise clap-like snare with slight reverb
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.06}},
         [_reverb(0.4, 0.18)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N]),
    # Ghost on step 2 and 14 (before beats 1 and 4)
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.10, 'sustain': 0, 'release': 0.06}},
         [_dist(0.55, 0.52)],
         [_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N,
          _N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,'C2',_N]),
]

# Hi-hat patterns — _vel_groove applied at generation time for groove feel.
_HIHATS = [
    # Straight 16ths — velocity does all the groove work
    _cfg('hihat', 'hihat', -6, '16n', 'MetalSynth',
         {'frequency': 800, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.006}, 'harmonicity': 8.5, 'modulationIndex': 55, 'resonance': 7000, 'octaves': 2.0},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # Breathing gap on beat 3 of bar 2 for micro-breakdown feel
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.01, 'release': 0.005}, 'harmonicity': 9.5, 'modulationIndex': 60, 'resonance': 8000, 'octaves': 2.2},
         [],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',
          'C4','C4',_N,'C4','C4','C4',_N,'C4',_N,_N,_N,_N,'C4',_N,'C4','C4']),
    # Distorted 16ths — raw texture
    _cfg('hihat', 'hihat', -6, '16n', 'MetalSynth',
         {'frequency': 1100, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.007}, 'harmonicity': 11, 'modulationIndex': 70, 'resonance': 10000, 'octaves': 2.5},
         [_dist(0.3, 0.3)],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4',
          'C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 8th-note pattern — sparse, lets kick breathe
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 750, 'envelope': {'attack': 0.001, 'decay': 0.014, 'release': 0.008}, 'harmonicity': 8.0, 'modulationIndex': 52, 'resonance': 6500, 'octaves': 1.9},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,
          'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # Irregular — skips create instability
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 850, 'envelope': {'attack': 0.001, 'decay': 0.011, 'release': 0.006}, 'harmonicity': 9.0, 'modulationIndex': 58, 'resonance': 7500, 'octaves': 2.1},
         [_dist(0.25, 0.25)],
         ['C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',
          'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4',_N,'C4','C4']),
    # Sparser 16ths with open-hat feel (longer decay)
    _cfg('hihat', 'hihat', -8, '16n', 'MetalSynth',
         {'frequency': 950, 'envelope': {'attack': 0.001, 'decay': 0.028, 'release': 0.014}, 'harmonicity': 10, 'modulationIndex': 64, 'resonance': 8500, 'octaves': 2.3},
         [],
         ['C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,'C4',_N,_N,
          'C4',_N,_N,'C4',_N,'C4',_N,_N,'C4',_N,_N,'C4',_N,_N,'C4',_N]),
    # Dense triplet-approximation feel — syncopated holes
    _cfg('hihat', 'hihat', -7, '16n', 'MetalSynth',
         {'frequency': 820, 'envelope': {'attack': 0.001, 'decay': 0.013, 'release': 0.006}, 'harmonicity': 8.8, 'modulationIndex': 56, 'resonance': 7200, 'octaves': 2.05},
         [],
         ['C4','C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,'C4',_N,'C4','C4',_N,
          'C4','C4',_N,'C4','C4',_N,_N,'C4','C4',_N,'C4','C4',_N,'C4',_N,'C4']),
]

# Acid bass lines — MonoSynth sawtooth, tight filter envelope for 303 zip character.
_ACID_BASSES = [
    # A minor — with filter automation for sweeping cutoff
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.05, 'baseFrequency': 80, 'octaves': 5.0}},
         [_dist(0.5, 0.5), _filt('lowpass', 600, 8)],
         ['A2','A2',_N,'A2','A2','A2',_N,'A2',_N,'A2','A2',_N,'C3','C3',_N,'A2',
          'A2','A2',_N,'A2','A2',_N,'A2',_N,'G2','G2','A2',_N,'E2',_N,'G2',_N],
         automation=[_auto('effect:1:frequency', 180, 3200, 'tri')]),
    # E minor — octave jumps, filter sweep
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.04},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.04, 'baseFrequency': 90, 'octaves': 5.5}},
         [_dist(0.55, 0.55), _filt('lowpass', 700, 10)],
         ['E2','E3',_N,'E2','E2','E3',_N,'E2',_N,'G2','E3','E2','B2',_N,'E2',_N,
          'E2','E3',_N,'E2','E2',_N,'D2','D3','E2',_N,'B1',_N,'D2','E2',_N,_N],
         automation=[_auto('effect:1:frequency', 200, 4000, 'tri')]),
    # D with chromatic passing tones
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0.0, 'release': 0.05},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.05, 'baseFrequency': 75, 'octaves': 4.8}},
         [_dist(0.6, 0.58)],
         ['D2',_N,'D2','Eb2','D2',_N,'C2','D2','D2',_N,'E2','D2',_N,'C#2','D2',_N,
          'D2',_N,'F2','E2','D2',_N,'C2',_N,'D2','Eb2','E2',_N,'F2',_N,'E2','D2']),
    # Rapid-fire A accent
    _cfg('bass', 'bass', -4, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.03},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.04, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 85, 'octaves': 5.5}},
         [_dist(0.65, 0.6)],
         ['A2','A2','A2',_N,'A2','A2',_N,'A2','A2',_N,'A2','A2',_N,'A2','A2',_N,
          'A2','A2','A2',_N,'C3','C3',_N,'A2','A2',_N,'A2','G2','A2',_N,'E2','A2',_N]),
    # G open filter
    _cfg('bass', 'bass', -3, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.04, 'release': 0.06},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0.02, 'release': 0.06, 'baseFrequency': 100, 'octaves': 4.2}},
         [_dist(0.45, 0.45)],
         ['G2',_N,'G2','A2','G2',_N,'F2','G2',_N,'G2','A2','G2','F2',_N,'G2',_N,
          'G2',_N,'G2','Bb2','A2',_N,'G2',_N,'F2','G2',_N,'E2','F2','G2',_N,_N]),
    # B tight envelope — filter automation builds intensity
    _cfg('bass', 'bass', -5, '16n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.045, 'sustain': 0.0, 'release': 0.025},
          'filterEnvelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0.0, 'release': 0.025, 'baseFrequency': 70, 'octaves': 6.0}},
         [_dist(0.7, 0.65), _filt('lowpass', 500, 7)],
         ['B1','B2','B1',_N,'B1','B2',_N,'B1','B1',_N,'B2','B1',_N,'B2','B1',_N,
          'B1','B2','B1',_N,'A1','B1',_N,'G#1','B1',_N,'A1',_N,'B1','A1',_N,_N],
         automation=[_auto('effect:1:frequency', 150, 3500, 'ramp')]),
]

# Acid leads — hypnotic cell-based patterns, texture/filter driven.
# Each is a MonoSynth with tight per-note filter zip, plus a global filter for automation.
_MONO_ACID = {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0.0, 'release': 0.04},
              'filterEnvelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0.0, 'release': 0.05, 'baseFrequency': 90, 'octaves': 5.5}}
_MONO_ACID_TIGHT = {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.03},
                    'filterEnvelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0.0, 'release': 0.03, 'baseFrequency': 80, 'octaves': 6.5}}

_LEADS = [
    # A2 pulse — single root note, filter sweep does all the talking
    _cfg('lead', 'lead', -10, '16n', 'MonoSynth',
         _MONO_ACID,
         [_dist(0.45, 0.5), _filt('lowpass', 500, 8)],
         ['A2','A2',_N,_N,'A2',_N,_N,_N,'A2',_N,'A2',_N,_N,_N,_N,_N,
          'A2','A2',_N,_N,'A2',_N,_N,_N,'A3',_N,_N,_N,'A2',_N,_N,_N],
         automation=[_auto('effect:1:frequency', 140, 3800, 'tri')]),
    # E2 stepping — sparse and repetitive, delay for hypnotic echo
    _cfg('lead', 'lead', -11, '16n', 'MonoSynth',
         _MONO_ACID_TIGHT,
         [_dist(0.5, 0.5), _delay('8n', 0.28, 0.2), _filt('lowpass', 600, 10)],
         ['E2',_N,_N,'E2','E2',_N,'E2',_N,'E3',_N,'E2',_N,_N,_N,_N,_N,
          'E2',_N,_N,'E2',_N,'E2',_N,_N,'E2',_N,'E3','E2',_N,_N,_N,_N],
         automation=[_auto('effect:2:frequency', 200, 4200, 'tri')]),
    # G grinding — dense cell, filter ramps up for building intensity
    _cfg('lead', 'lead', -10, '16n', 'MonoSynth',
         _MONO_ACID,
         [_dist(0.55, 0.55), _filt('lowpass', 350, 6)],
         ['G2','G2','G2',_N,'G2','G2',_N,'G2','G2',_N,'G2',_N,'G2',_N,_N,_N,
          'G2','G2',_N,'G2','G2',_N,_N,'G2',_N,'G2',_N,_N,'G2',_N,_N,_N],
         automation=[_auto('effect:1:frequency', 120, 3000, 'ramp')]),
    # B1 drone — minimal movement, almost a texture
    _cfg('lead', 'lead', -11, '16n', 'MonoSynth',
         _MONO_ACID_TIGHT,
         [_dist(0.6, 0.6), _filt('lowpass', 400, 9)],
         ['B1',_N,'B1',_N,_N,'B1',_N,_N,'B1',_N,_N,_N,'B2',_N,_N,_N,
          'B1',_N,'B1',_N,_N,_N,'B1',_N,_N,'B1',_N,_N,_N,_N,_N,_N],
         automation=[_auto('effect:1:frequency', 160, 3500, 'tri')]),
]


class AcidTechnoTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.ACID_TECHNO
    BPM_RANGE = (133, 140)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_ACID_BASSES))

        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.25)

        layers = [kick, snare, hihat, bass]

        # Lead enters immediately or after 2-4 loops for arrangement variety.
        # dropout_prob gives the hi-hat a chance to temporarily vanish.
        if random.random() < 0.65:
            lead = copy.deepcopy(cls._pick(_LEADS))
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.3, ghost_prob=0.08)
            lead['entry_loop'] = random.choice([0, 0, 2, 4])
            layers.append(lead)

        if random.random() < 0.4:
            hihat['dropout_prob'] = random.choice([0.2, 0.25, 0.3])

        return layers

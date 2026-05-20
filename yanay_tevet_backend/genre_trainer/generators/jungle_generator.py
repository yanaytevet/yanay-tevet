import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, _N, _cfg, _dist, _reverb, _delay, _filt,
    _vel, _vel_groove, _vel_kick, _vel_snare,
)

_KICKS = [
    # Syncopated amen-style: kick on 1, quick double before 2, 3, syncopated before 4
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0.01, 'release': 0.65}},
         [],
         ['C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N]),
    # More off-beat, irregular pattern
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.038, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0.01, 'release': 0.6}},
         [],
         ['C1',_N,'C1',_N,_N,'C1',_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,'C1',_N,'C1',_N,_N]),
    # Double-time feel, lots of kicks
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.042, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0.01, 'release': 0.55}},
         [],
         ['C1',_N,_N,_N,'C1',_N,'C1',_N,'C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,'C1',_N,_N,_N,_N]),
    # Sparse rave kick feel
    _cfg('kick', 'kick', 2, '8n', 'MembraneSynth',
         {'pitchDecay': 0.045, 'octaves': 9, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0.01, 'release': 0.7}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N]),
    # Two-bar roll pattern
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.036, 'octaves': 11, 'envelope': {'attack': 0.001, 'decay': 0.19, 'sustain': 0.01, 'release': 0.58}},
         [],
         ['C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N,'C1',_N,_N,'C1','C1',_N,'C1',_N,'C1',_N,'C1',_N,'C1',_N,_N,'C1',_N,_N,_N,_N]),
    # Shuffled syncopated
    _cfg('kick', 'kick', 1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.04, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.21, 'sustain': 0.01, 'release': 0.62}},
         [],
         ['C1','C1',_N,_N,'C1',_N,_N,'C1','C1',_N,_N,_N,'C1',_N,_N,_N,'C1','C1',_N,_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,_N]),
    # Driving amen variation
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.043, 'octaves': 10, 'envelope': {'attack': 0.001, 'decay': 0.23, 'sustain': 0.01, 'release': 0.68}},
         [],
         ['C1',_N,_N,'C1',_N,_N,'C1',_N,'C1',_N,_N,_N,'C1',_N,'C1',_N,'C1',_N,_N,'C1',_N,'C1',_N,_N,'C1',_N,_N,_N,'C1',_N,_N,_N]),
]

_SNARES = [
    # Classic off-beat snare (2 and 4)
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.09, 'sustain': 0, 'release': 0.06}},
         [_dist(0.3, 0.3)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,'C2',_N,'C2',_N,_N,_N]),
    # Double snare + ghost notes
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.08, 'sustain': 0, 'release': 0.05}},
         [_dist(0.28, 0.28)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,'C2','C2',_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,'C2',_N,_N,'C2','C2',_N,_N]),
    # Snare roll pattern (amen feel)
    _cfg('snare', 'snare', -3, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.07, 'sustain': 0, 'release': 0.04}},
         [_dist(0.32, 0.32)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N,_N,_N,'C2',_N,_N,_N,'C2',_N,_N,'C2',_N,_N,'C2',_N]),
    # Pink noise snare with reverb
    _cfg('snare', 'snare', -4, '16n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.1, 'sustain': 0, 'release': 0.07}},
         [_reverb(0.5, 0.2)],
         [_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,_N,_N,_N,_N,'C2',_N,_N,_N,'C2',_N,_N,_N,'C2',_N,'C2',_N]),
    # Rapid ghost-note snare
    _cfg('snare', 'snare', -5, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.06, 'sustain': 0, 'release': 0.04}},
         [],
         [_N,_N,_N,'C2','C2',_N,_N,_N,_N,'C2',_N,_N,'C2',_N,'C2',_N,_N,_N,_N,'C2','C2',_N,_N,_N,_N,'C2',_N,_N,'C2',_N,'C2',_N]),
]

_HIHATS = [
    # Fast 16ths (jungle speed)
    _cfg('hihat', 'hihat', -8, '16n', 'MetalSynth',
         {'frequency': 1000, 'envelope': {'attack': 0.001, 'decay': 0.008, 'release': 0.005}, 'harmonicity': 10.0, 'modulationIndex': 60, 'resonance': 9000, 'octaves': 2.4},
         [],
         ['C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4','C4']),
    # 16ths with gaps
    _cfg('hihat', 'hihat', -8, '16n', 'MetalSynth',
         {'frequency': 1100, 'envelope': {'attack': 0.001, 'decay': 0.009, 'release': 0.005}, 'harmonicity': 11.0, 'modulationIndex': 65, 'resonance': 10000, 'octaves': 2.6},
         [],
         ['C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4','C4',_N,'C4','C4']),
    # Open hihat feel (longer decay = "open")
    _cfg('hihat', 'hihat', -9, '16n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.05, 'release': 0.03}, 'harmonicity': 9.5, 'modulationIndex': 58, 'resonance': 8500, 'octaves': 2.2},
         [],
         ['C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N,'C4',_N]),
    # Syncopated 16ths with accent
    _cfg('hihat', 'hihat', -8, '16n', 'MetalSynth',
         {'frequency': 1200, 'envelope': {'attack': 0.001, 'decay': 0.007, 'release': 0.004}, 'harmonicity': 12.0, 'modulationIndex': 72, 'resonance': 11000, 'octaves': 2.8},
         [],
         ['C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4','C4','C4','C4',_N,'C4','C4','C4',_N,'C4','C4',_N,'C4','C4',_N,'C4','C4']),
]

_BASSES = [
    # Classic rave sub bass, A
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.01, 'decay': 0.25, 'sustain': 0.7, 'release': 0.3}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.3, 'sustain': 0.65, 'release': 0.28, 'baseFrequency': 55, 'octaves': 1.0}},
         [],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,'A0',_N,_N,_N,'E0',_N,_N,_N]),
    # Wobbly reese-style bass
    _cfg('bass', 'bass', -2, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.008, 'decay': 0.3, 'sustain': 0.65, 'release': 0.32}, 'filterEnvelope': {'attack': 0.008, 'decay': 0.4, 'sustain': 0.6, 'release': 0.3, 'baseFrequency': 60, 'octaves': 2.5}},
         [_filt('lowpass', 600, 5)],
         ['D1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'C1',_N,_N,_N,'D1',_N,_N,_N,'D1',_N,_N,_N,'A0',_N,_N,_N,'D1',_N,_N,_N]),
    # Punchy E, syncopated rhythm
    _cfg('bass', 'bass', 1, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.005, 'decay': 0.18, 'sustain': 0.75, 'release': 0.22}, 'filterEnvelope': {'attack': 0.005, 'decay': 0.22, 'sustain': 0.7, 'release': 0.2, 'baseFrequency': 52, 'octaves': 1.2}},
         [],
         ['E1',_N,_N,'E1',_N,_N,'E1',_N,'E1',_N,_N,_N,'B0',_N,_N,_N,'E1',_N,'E1',_N,_N,_N,'E1',_N,'D1',_N,_N,_N,'E1',_N,_N,_N]),
    # G minor groove
    _cfg('bass', 'bass', 0, '8n', 'MonoSynth',
         {'oscillator': {'type': 'sine'}, 'envelope': {'attack': 0.01, 'decay': 0.22, 'sustain': 0.72, 'release': 0.28}, 'filterEnvelope': {'attack': 0.01, 'decay': 0.28, 'sustain': 0.67, 'release': 0.25, 'baseFrequency': 58, 'octaves': 1.1}},
         [],
         ['G0',_N,_N,_N,'G0',_N,_N,_N,'G0',_N,_N,_N,'F0',_N,_N,_N,'G0',_N,_N,_N,'Bb0',_N,_N,_N,'A0',_N,_N,_N,'G0',_N,_N,_N]),
    # FMSynth growl bass
    _cfg('bass', 'bass', -3, '8n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 8, 'envelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 0.6, 'release': 0.25}, 'modulationEnvelope': {'attack': 0.008, 'decay': 0.15, 'sustain': 0.4, 'release': 0.22}},
         [_filt('lowpass', 700, 3)],
         ['A0',_N,_N,_N,'A0',_N,_N,_N,'E1',_N,_N,_N,'D1',_N,_N,_N,'A0',_N,_N,_N,'A0',_N,_N,_N,'G0',_N,_N,_N,'A0',_N,_N,_N]),
]

_PADS = [
    _cfg('pad', 'pad', -16, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.7, 'release': 1.5}},
         [_reverb(4.5, 0.8), _filt('lowpass', 2000, 2)],
         ['A3',_N,_N,_N,_N,_N,_N,_N,'C4',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -17, '16n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.4, 'decay': 0.3, 'sustain': 0.75, 'release': 1.8}, 'modulationEnvelope': {'attack': 0.6, 'decay': 0.2, 'sustain': 0.8, 'release': 1.5}},
         [_reverb(5.0, 0.82)],
         ['E3',_N,_N,_N,_N,_N,_N,_N,'G3',_N,_N,_N,_N,_N,_N,_N,'B3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N]),
    _cfg('pad', 'pad', -16, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'}, 'envelope': {'attack': 0.5, 'decay': 0.4, 'sustain': 0.72, 'release': 2.0}},
         [_reverb(5.5, 0.85)],
         ['D3',_N,_N,_N,_N,_N,_N,_N,'F3',_N,_N,_N,_N,_N,_N,_N,'A3',_N,_N,_N,_N,_N,_N,_N,'E3',_N,_N,_N,_N,_N,_N,_N]),
]


class JungleTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.JUNGLE
    BPM_RANGE = (160, 170)

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        # Amen feel: velocity variance is what gives the broken pattern its life
        kick['pattern']['velocities'] = _vel_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        bass['pattern']['velocities'] = _vel(bass['pattern']['steps'], accent_prob=0.2, ghost_prob=0.08)

        layers = [kick, snare, hihat, bass]

        if random.random() < 0.4:
            pad = copy.deepcopy(cls._pick(_PADS))
            pad['entry_loop'] = random.choice([0, 2])
            layers.append(pad)

        return layers

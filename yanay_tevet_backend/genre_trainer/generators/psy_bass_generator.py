import copy
import random
from typing import Any

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import (
    BaseTrackGenerator, GenreProfile, _N, _cfg, _auto, _chorus, _delay, _dist, _filt, _pingpong, _reverb, _wobble,
    _midi_to_note, _note_to_midi, _vel, _vel_groove, _vel_snare, _on, _at,
)


def _vel_halftime_kick(steps: list) -> list[float | None]:
    """The kick on the one of each bar hits hardest; the syncopated second kick sits just under it,
    which is what makes the slow beat lurch rather than march."""
    vels: list[float | None] = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 16 == 0:
            vels.append(round(random.uniform(0.9, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.68, 0.85), 2))
    return vels


# MIDI D1. Every sub note is folded into the octave above it (37–69 Hz): low enough to sit under
# the wobble, high enough to still be heard on small speakers.
_SUB_FLOOR = 26


def _sub_under(bass: dict[str, Any]) -> dict[str, Any]:
    """A clean sine sub doubling the wobble line. The wobble's filter sweeps the low end in and out;
    the sub keeps the weight constant under it."""
    steps = [_N if s is None else _midi_to_note(_SUB_FLOOR + (_note_to_midi(s) - _SUB_FLOOR) % 12)
             for s in bass['pattern']['steps']]
    return _cfg('sub', 'sub', -9, bass['note_duration'], 'Synth',
                {'oscillator': {'type': 'sine'},
                 'envelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 1.0, 'release': 0.15}},
                [], steps, velocities=[_N if s is None else 0.85 for s in steps],
                sidechain='shallow')


# ---------------------------------------------------------------------------
# KICKS — slow, swung glitch-hop: a kick on the one plus a syncopated second
# kick (the "a" of 2 or the "and" of 3) against the snare on 2 and 4. Never
# four-on-the-floor — that would make it psytrance. Round, deep kicks with a
# longer tail, since at ~105 BPM there is room between hits.
# ---------------------------------------------------------------------------
_KICKS = [
    # K . . . S . . . . . K . S . . . | same — the half-time two-step
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.45, 'sustain': 0.01, 'release': 1.0}},
         [], _on([0, 10, 16, 26], 'C1')),
    # Second kick on the "a" of 2 (step 7), bar 2 adds the "and" of 3
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.065, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.48, 'sustain': 0.01, 'release': 1.1}},
         [], _on([0, 7, 16, 23, 26], 'C1')),
    # 0 + 7 + 10 — the lurching glitch-hop kick, plain answer in bar 2
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.055, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.42, 'sustain': 0.01, 'release': 0.9}},
         [_dist(0.15, 0.2)], _on([0, 7, 10, 16, 26], 'C1')),
    # Dotted lead (0, 3) into the "and" of 3, with a pickup at the end of bar 2
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.06, 'octaves': 6.5, 'envelope': {'attack': 0.001, 'decay': 0.4, 'sustain': 0.01, 'release': 0.9}},
         [], _on([0, 3, 10, 16, 26, 30], 'C1')),
    # Bar 2 skips through the "a" of 1 and the "and" of 2 before landing on the "and" of 3
    _cfg('kick', 'kick', 0, '8n', 'MembraneSynth',
         {'pitchDecay': 0.07, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.5, 'sustain': 0.01, 'release': 1.2}},
         [], _on([0, 10, 16, 19, 22, 26], 'C1')),
    # Double "and" of 3 (10 + 11) in bar 1 — a stumble that the swing exaggerates
    _cfg('kick', 'kick', -1, '8n', 'MembraneSynth',
         {'pitchDecay': 0.058, 'octaves': 7, 'envelope': {'attack': 0.001, 'decay': 0.44, 'sustain': 0.01, 'release': 1.0}},
         [_dist(0.12, 0.18)], _on([0, 10, 11, 16, 23], 'C1')),
]

# ---------------------------------------------------------------------------
# SNARES — heavy backbeat on 2 and 4 (steps 4, 12, 20, 28), long and drenched
# in reverb: at half the tempo of DnB the snare tail is part of the groove.
# Variation is only in the ghost notes.
# ---------------------------------------------------------------------------
_SNARES = [
    # . . . . S . . . . . . . S . . . | same — the plain heavy backbeat
    _cfg('snare', 'snare', -2, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.24, 'sustain': 0, 'release': 0.12}},
         [_filt('highpass', 650, 0.7), _reverb(2.2, 0.35, 0.01)],
         _on([4, 12, 20, 28])),
    # Ghost on the "and" of 4 at the end of the loop
    _cfg('snare', 'snare', -2, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.26, 'sustain': 0, 'release': 0.12}},
         [_filt('highpass', 600, 0.7), _reverb(2.5, 0.38, 0.015)],
         _on([4, 12, 20, 28, 30])),
    # Pickup ghost on the last 16th of bar 1
    _cfg('snare', 'snare', -3, '8n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.28, 'sustain': 0, 'release': 0.14}},
         [_filt('highpass', 500, 0.7), _reverb(2.8, 0.4, 0.02)],
         _on([4, 12, 15, 20, 28])),
    # Flam-like ghost a 16th before the last backbeat
    _cfg('snare', 'snare', -2, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.22, 'sustain': 0, 'release': 0.1}},
         [_filt('highpass', 700, 0.7), _reverb(2.0, 0.34, 0.01)],
         _on([4, 12, 20, 27, 28])),
    # Ghosts on the "e" of 3 and the last 16th of bar 2
    _cfg('snare', 'snare', -3, '8n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.12}},
         [_filt('highpass', 620, 0.7), _reverb(2.4, 0.36, 0.012)],
         _on([4, 9, 12, 20, 28, 31])),
    # Double after the last backbeat — a swung "ka-tak"
    _cfg('snare', 'snare', -2, '8n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.27, 'sustain': 0, 'release': 0.13}},
         [_filt('highpass', 560, 0.7), _reverb(2.6, 0.38, 0.02)],
         _on([4, 12, 14, 20, 28, 29])),
]

# ---------------------------------------------------------------------------
# SNARE BODIES — a fat, low-tuned membrane under the backbeat so the snare
# hits with weight, not just noise.
# ---------------------------------------------------------------------------
_SNARE_BODIES = [
    _cfg('snare_body', 'snare', -8, '16n', 'MembraneSynth',
         {'pitchDecay': 0.03, 'octaves': 2.5, 'envelope': {'attack': 0.001, 'decay': 0.18, 'sustain': 0, 'release': 0.08}},
         [_reverb(1.8, 0.25)], _on([4, 12, 20, 28], 'E3')),
    _cfg('snare_body', 'snare', -8, '16n', 'MembraneSynth',
         {'pitchDecay': 0.035, 'octaves': 2, 'envelope': {'attack': 0.001, 'decay': 0.2, 'sustain': 0, 'release': 0.08}},
         [_reverb(2.0, 0.28)], _on([4, 12, 20, 28], 'D3')),
    _cfg('snare_body', 'snare', -9, '16n', 'MembraneSynth',
         {'pitchDecay': 0.025, 'octaves': 3, 'envelope': {'attack': 0.001, 'decay': 0.16, 'sustain': 0, 'release': 0.07}},
         [_reverb(1.6, 0.22)], _on([4, 12, 20, 28], 'G3')),
]

# ---------------------------------------------------------------------------
# HI-HATS — tight hats the transport swing pushes into a lazy shuffle; kept
# quieter than the glitch percussion so the stutters stand out.
# ---------------------------------------------------------------------------
_HIHATS = [
    # Swung 8ths
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 420, 'envelope': {'attack': 0.001, 'decay': 0.04, 'release': 0.02},
          'harmonicity': 5.1, 'modulationIndex': 32, 'resonance': 7000, 'octaves': 1.5},
         [], _on(list(range(0, 32, 2)), 'C4')),
    # Swung 16ths with gaps — the shuffle of glitch-hop
    _cfg('hihat', 'hihat', -17, '16n', 'MetalSynth',
         {'frequency': 460, 'envelope': {'attack': 0.001, 'decay': 0.03, 'release': 0.015},
          'harmonicity': 5.4, 'modulationIndex': 36, 'resonance': 7600, 'octaves': 1.6},
         [], _on([0, 2, 3, 6, 7, 8, 10, 11, 14, 16, 18, 19, 22, 24, 26, 27, 30, 31], 'C4')),
    # Offbeat 8ths with a 16th pickup into each bar
    _cfg('hihat', 'hihat', -16, '16n', 'MetalSynth',
         {'frequency': 380, 'envelope': {'attack': 0.001, 'decay': 0.07, 'release': 0.04},
          'harmonicity': 5.1, 'modulationIndex': 30, 'resonance': 6500, 'octaves': 1.4},
         [], _on([2, 6, 10, 14, 15, 18, 22, 26, 30, 31], 'C4')),
    # Full swung 16ths, very quiet — a ticking bed
    _cfg('hihat', 'hihat', -19, '16n', 'MetalSynth',
         {'frequency': 500, 'envelope': {'attack': 0.001, 'decay': 0.025, 'release': 0.012},
          'harmonicity': 5.8, 'modulationIndex': 40, 'resonance': 8200, 'octaves': 1.6},
         [], _on(list(range(32)), 'C4')),
    # Shaker 16ths
    _cfg('shaker', 'hihat', -19, '16n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.002, 'decay': 0.05, 'sustain': 0, 'release': 0.02}},
         [_filt('highpass', 5500, 0.7)], _on(list(range(32)), 'C4')),
]

# ---------------------------------------------------------------------------
# GLITCHES — 32nd-note stutters (subdivision '32n': 64 steps, step 2n lines up
# with 16th step n). Short bursts of clicks, zips and bleeps between the kick
# and snare: the "glitch" of glitch-hop and Tipper-style bass music.
# ---------------------------------------------------------------------------
_GLITCHES = [
    # Metallic click bursts before beat 2 of bar 1 and through the end of bar 2
    _cfg('glitch', 'perc', -17, '32n', 'MetalSynth',
         {'frequency': 900, 'envelope': {'attack': 0.001, 'decay': 0.012, 'release': 0.008},
          'harmonicity': 8.1, 'modulationIndex': 20, 'resonance': 5000, 'octaves': 1.2},
         [_pingpong('16n', 0.3, 0.2)],
         _on([12, 13, 14, 15, 44, 45, 46, 56, 57, 58, 59, 60, 61, 62, 63], 'C5', 64), subdivision='32n', pan=0.3),
    # Band-passed noise "zips" in threes
    _cfg('glitch', 'perc', -16, '32n', 'NoiseSynth',
         {'noise': {'type': 'white'}, 'envelope': {'attack': 0.001, 'decay': 0.015, 'sustain': 0, 'release': 0.01}},
         [_filt('bandpass', 3200, 4), _pingpong('8n', 0.25, 0.2)],
         _on([21, 22, 23, 37, 38, 39, 53, 54, 55, 61, 62, 63], 'C4', 64), subdivision='32n', pan=-0.3),
    # Pitched bleeps — tiny membrane blips stuttering like a cut-up sample
    _cfg('glitch', 'perc', -18, '32n', 'MembraneSynth',
         {'pitchDecay': 0.008, 'octaves': 1.5, 'envelope': {'attack': 0.001, 'decay': 0.035, 'sustain': 0, 'release': 0.02}},
         [_delay('16n', 0.3, 0.2)],
         _on([6, 7, 26, 27, 28, 29, 46, 47, 58, 59, 60, 61, 62, 63], 'C6', 64), subdivision='32n', pan=0.25),
    # Ratchets leading into each backbeat of bar 2
    _cfg('glitch', 'perc', -17, '32n', 'MetalSynth',
         {'frequency': 650, 'envelope': {'attack': 0.001, 'decay': 0.015, 'release': 0.01},
          'harmonicity': 6.3, 'modulationIndex': 24, 'resonance': 4500, 'octaves': 1.3},
         [_filt('highpass', 2500, 0.7)],
         _on([37, 38, 39, 53, 54, 55], 'C5', 64), subdivision='32n', pan=-0.2),
    # A dense granular smear across beat 3 of bar 2
    _cfg('glitch', 'perc', -20, '32n', 'NoiseSynth',
         {'noise': {'type': 'pink'}, 'envelope': {'attack': 0.001, 'decay': 0.02, 'sustain': 0, 'release': 0.01}},
         [_filt('bandpass', 1800, 3), _reverb(1.2, 0.25)],
         _on([40, 41, 42, 43, 44, 45, 46, 47], 'C4', 64), subdivision='32n'),
]

# ---------------------------------------------------------------------------
# BASSES — the wobble: a saw / square / FM tone held for long notes (8n to 2n)
# through a tempo-synced filter LFO (_wobble), so the filter "talks" in time
# with the beat. Rates vary across entries ('8n', '8t', '16n', '4n') and so do
# the LFO shapes; the synth's own filter is left open so the wobble does the
# shaping. Distortion before the wobble feeds it harmonics to sweep. Every line
# puts its root first and most often, which key coherence locks to.
# ---------------------------------------------------------------------------


def _open_mono(osc: dict[str, Any]) -> dict[str, Any]:
    return {'oscillator': osc,
            'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.9, 'release': 0.2},
            'filterEnvelope': {'attack': 0.005, 'decay': 0.2, 'sustain': 1.0, 'release': 0.2,
                               'baseFrequency': 2400, 'octaves': 1}}


_BASSES = [
    # A minor saw, 8th-note wobble — the root held through the two-step, up to the 3rd in bar 2
    _cfg('wobble_bass', 'bass', -6, '2n', 'MonoSynth', _open_mono({'type': 'sawtooth'}),
         [_dist(0.35, 0.3), _wobble('8n', 90, 5, 6)],
         _at({0: 'A1', 10: 'A1', 16: 'A1', 22: 'C2', 26: 'G1'})),
    # D minor FM growl, triplet wobble — the rolling, Tipper-ish "yoy" against the swung beat
    _cfg('wobble_bass', 'bass', -7, '2n', 'FMSynth',
         {'harmonicity': 0.5, 'modulationIndex': 10, 'oscillator': {'type': 'sine'}, 'modulation': {'type': 'square'},
          'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.9, 'release': 0.2},
          'modulationEnvelope': {'attack': 0.02, 'decay': 0.3, 'sustain': 0.7, 'release': 0.2}},
         [_dist(0.4, 0.35), _wobble('8t', 120, 4.5, 5)],
         _at({0: 'D2', 7: 'F2', 10: 'D2', 16: 'D2', 26: 'C2'})),
    # G minor square, 16th wobble with a triangle LFO — a fast, buzzing flutter
    _cfg('wobble_bass', 'bass', -8, '4n', 'MonoSynth', _open_mono({'type': 'square'}),
         [_dist(0.3, 0.25), _wobble('16n', 100, 4, 7, shape='triangle')],
         _at({0: 'G1', 8: 'G1', 14: 'Bb1', 16: 'G1', 24: 'F1', 28: 'D2'})),
    # C minor detuned saws, quarter-note wobble — slow yawning sweeps over long notes
    _cfg('wobble_bass', 'bass', -7, '2n', 'MonoSynth', _open_mono({'type': 'fatsawtooth', 'count': 2, 'spread': 16}),
         [_dist(0.25, 0.25), _wobble('4n', 70, 5.5, 8), _chorus(0.5, 3, 0.4, 0.25)],
         _at({0: 'C2', 10: 'C2', 16: 'Ab1', 24: 'Bb1'})),
    # F minor FM, square-LFO wobble on 8ths — a gated, choppy "wub-wub"
    _cfg('wobble_bass', 'bass', -7, '4n', 'FMSynth',
         {'harmonicity': 1.0, 'modulationIndex': 6, 'oscillator': {'type': 'sawtooth'}, 'modulation': {'type': 'sine'},
          'envelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.9, 'release': 0.2},
          'modulationEnvelope': {'attack': 0.01, 'decay': 0.2, 'sustain': 0.8, 'release': 0.2}},
         [_dist(0.3, 0.3), _wobble('8n', 150, 4, 4, shape='square')],
         _at({0: 'F1', 6: 'F1', 10: 'Ab1', 16: 'F1', 22: 'F1', 26: 'Eb2'})),
    # B minor saw, triplet wobble — root pushed on the kick, a lift to the 3rd, falling to the 5th
    _cfg('wobble_bass', 'bass', -6, '4n', 'MonoSynth', _open_mono({'type': 'sawtooth'}),
         [_dist(0.4, 0.3), _wobble('8t', 85, 5, 6, shape='triangle')],
         _at({0: 'B1', 10: 'B1', 14: 'D2', 16: 'B1', 26: 'A1', 30: 'F#1'})),
    # A minor metallic FM mid-bass, 16th wobble — shorter notes, the glitchy Tipper end
    _cfg('wobble_bass', 'bass', -8, '8n', 'FMSynth',
         {'harmonicity': 2.0, 'modulationIndex': 4, 'oscillator': {'type': 'square'}, 'modulation': {'type': 'triangle'},
          'envelope': {'attack': 0.005, 'decay': 0.15, 'sustain': 0.85, 'release': 0.15},
          'modulationEnvelope': {'attack': 0.005, 'decay': 0.12, 'sustain': 0.6, 'release': 0.15}},
         [_dist(0.35, 0.3), _wobble('16n', 110, 4.5, 6)],
         _at({0: 'A1', 3: 'A1', 10: 'C2', 16: 'A1', 19: 'A1', 26: 'E2'})),
]

# ---------------------------------------------------------------------------
# ZAPS — pitch-swept sci-fi zaps through ping-pong delays, the psychedelic
# sound effects of the genre. A membrane with a long pitch decay dives from
# high to low; the portamento synth glides up instead.
# ---------------------------------------------------------------------------
_ZAPS = [
    # Laser dive on the "and" of 2 in both bars
    _cfg('zap', 'perc', -18, '16n', 'MembraneSynth',
         {'pitchDecay': 0.22, 'octaves': 8, 'envelope': {'attack': 0.001, 'decay': 0.25, 'sustain': 0, 'release': 0.1}},
         [_pingpong('8n', 0.4, 0.35), _reverb(2.5, 0.3)],
         _on([6, 22], 'C4'), pan=-0.2),
    # Rising glide zap into the last backbeat
    _cfg('zap', 'perc', -22, '16n', 'Synth',
         {'oscillator': {'type': 'sawtooth'}, 'portamento': 0.12,
          'envelope': {'attack': 0.005, 'decay': 0.1, 'sustain': 0.6, 'release': 0.1}},
         [_filt('bandpass', 1800, 2), _pingpong('8n.', 0.45, 0.35)],
         _at({26: 'C3', 27: 'C6'}), pan=0.25),
    # Short laser bursts scattered through the loop
    _cfg('zap', 'perc', -19, '16n', 'MembraneSynth',
         {'pitchDecay': 0.1, 'octaves': 6, 'envelope': {'attack': 0.001, 'decay': 0.12, 'sustain': 0, 'release': 0.06}},
         [_pingpong('16n', 0.35, 0.3)],
         _on([3, 11, 27, 30], 'G4'), pan=0.3),
    # One long dive bomb every other loop
    _cfg('zap', 'perc', -20, '4n', 'MembraneSynth',
         {'pitchDecay': 0.6, 'octaves': 16, 'envelope': {'attack': 0.001, 'decay': 0.8, 'sustain': 0, 'release': 0.3}},
         [_reverb(3.5, 0.45), _pingpong('4n', 0.4, 0.3)],
         _on([12], 'A2'), loop_modulo=2, loop_modulo_remainder=1),
]

# ---------------------------------------------------------------------------
# LEADS — sparse, delay-soaked plucks and bells in exotic modes (phrygian
# dominant, minor pentatonic): the "psy" in psybass. Tonic first and most often.
# ---------------------------------------------------------------------------
_LEADS = [
    # FM bell motif in A minor, thrown across a dotted ping-pong
    _cfg('lead', 'lead', -17, '16n', 'FMSynth',
         {'harmonicity': 3.01, 'modulationIndex': 10,
          'envelope': {'attack': 0.002, 'decay': 0.4, 'sustain': 0.0, 'release': 0.4},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.0, 'release': 0.3}},
         [_pingpong('8n.', 0.45, 0.35), _reverb(3.0, 0.4)],
         _at({2: 'A4', 6: 'E5', 11: 'C5', 18: 'A4', 24: 'G4'})),
    # Phrygian-dominant pluck in D — the Middle-Eastern flavour of Kalya Scintilla-style tracks
    _cfg('lead', 'lead', -18, '16n', 'Synth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 0.002, 'decay': 0.25, 'sustain': 0.0, 'release': 0.3}},
         [_delay('8t', 0.4, 0.3), _reverb(2.5, 0.35)],
         _at({0: 'D5', 3: 'Eb5', 6: 'F#5', 8: 'G5', 11: 'F#5', 14: 'Eb5', 16: 'D5', 28: 'D5'})),
    # Glassy AM blips in E minor pentatonic, high and far back
    _cfg('lead', 'lead', -20, '16n', 'AMSynth',
         {'harmonicity': 2.5,
          'envelope': {'attack': 0.002, 'decay': 0.2, 'sustain': 0.0, 'release': 0.3},
          'modulationEnvelope': {'attack': 0.002, 'decay': 0.15, 'sustain': 0.0, 'release': 0.2}},
         [_pingpong('16n', 0.5, 0.35), _reverb(3.5, 0.45)],
         _at({0: 'E5', 5: 'B5', 9: 'E5', 13: 'G5', 20: 'E5', 26: 'D5'})),
]

# ---------------------------------------------------------------------------
# PADS — washy, slowly filtered beds drenched in reverb and chorus behind the
# beat. Tonic chord first.
# ---------------------------------------------------------------------------
_PADS = [
    # Am(add9) -> Fmaj7 detuned saws, a slow lowpass sweep across the loop
    _cfg('pad', 'pad', -24, '1n', 'PolySynth',
         {'oscillator': {'type': 'fatsawtooth', 'count': 3, 'spread': 28},
          'envelope': {'attack': 1.0, 'decay': 0.5, 'sustain': 0.8, 'release': 3.0}},
         [_filt('lowpass', 1200, 0.8), _chorus(0.3, 4, 0.7, 0.5), _reverb(6.0, 0.7)],
         _at({0: 'A3,B3,C4,E4', 16: 'F3,A3,C4,E4'}),
         automation=[_auto('effect:0:frequency', 600, 2400, 'tri')]),
    # Dm9 wash in soft triangles
    _cfg('pad', 'pad', -23, '1n', 'PolySynth',
         {'oscillator': {'type': 'triangle'},
          'envelope': {'attack': 1.2, 'decay': 0.5, 'sustain': 0.8, 'release': 3.0}},
         [_chorus(0.4, 3.5, 0.6, 0.45), _reverb(7.0, 0.75)],
         _at({0: 'D3,F3,A3,C4,E4', 16: 'D3,F3,A3,C4'})),
    # AM drone on the root and fifth, echoing
    _cfg('pad', 'pad', -22, '2n', 'AMSynth',
         {'harmonicity': 0.5, 'envelope': {'attack': 0.8, 'decay': 0.4, 'sustain': 0.8, 'release': 2.5},
          'modulationEnvelope': {'attack': 1.0, 'decay': 0.3, 'sustain': 0.7, 'release': 2.0}},
         [_delay('4n', 0.45, 0.3), _reverb(5.0, 0.7)],
         _at({0: 'E3', 16: 'E3', 24: 'B2'})),
]


class PsyBassTrackGenerator(BaseTrackGenerator):
    GENRE = GenreType.PSY_BASS
    BPM_RANGE = (100, 110)
    LEVEL_DB = -4.6
    PROFILE = GenreProfile(
        drums='Slow, swung broken beat: kick on 1 plus a syncopated kick, heavy snare on 2 and 4',
        bass='Long notes that wobble in time with the beat',
        signature='Pitch-swept zaps, glitch stutters, Middle-Eastern plucks',
        mood='Heavy, psychedelic, laid-back',
        key_trait='bass',
        kick_pattern='halftime',
        bass_pattern='wobble',
    )
    SWING = 0.2  # Glitch-hop leans hard on the shuffle; it is half of what makes it groove at ~105 BPM
    KEY_ROLES = ('bass',)
    SIDECHAIN_DEPTH = 0.5
    SIDECHAIN_RELEASE = 0.5

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        kick = copy.deepcopy(cls._pick(_KICKS))
        snare = copy.deepcopy(cls._pick(_SNARES))
        body = copy.deepcopy(cls._pick(_SNARE_BODIES))
        hihat = copy.deepcopy(cls._pick(_HIHATS))
        bass = copy.deepcopy(cls._pick(_BASSES))

        kick['pattern']['velocities'] = _vel_halftime_kick(kick['pattern']['steps'])
        snare['pattern']['velocities'] = _vel_snare(snare['pattern']['steps'])
        body['pattern']['velocities'] = _vel_snare(body['pattern']['steps'])
        hihat['pattern']['velocities'] = _vel_groove(hihat['pattern']['steps'])
        # Held wobble notes want an even level; the LFO is the movement, not the velocity.
        bass['pattern']['velocities'] = [_N if s is None else round(random.uniform(0.8, 0.92), 2)
                                         for s in bass['pattern']['steps']]

        layers = [kick, snare, body, hihat, bass]

        glitch = cls._maybe(_GLITCHES, 0.8)
        if glitch:
            glitch = copy.deepcopy(glitch)
            glitch['pattern']['velocities'] = _vel(glitch['pattern']['steps'], accent_prob=0.25, ghost_prob=0.3)
            layers.append(glitch)

        zap = cls._maybe(_ZAPS, 0.6)
        if zap:
            layers.append(copy.deepcopy(zap))

        lead = cls._maybe(_LEADS, 0.45)
        if lead:
            lead = copy.deepcopy(lead)
            lead['pattern']['velocities'] = _vel(lead['pattern']['steps'], accent_prob=0.2, ghost_prob=0.1)
            lead['entry_loop'] = random.choice([0, 2, 4])
            layers.append(lead)

        pad = cls._maybe(_PADS, 0.5)
        if pad:
            layers.append(copy.deepcopy(pad))

        cls._apply_key_coherence(layers)
        # The sub is built from the bass after key coherence has moved it, so it is already in key and
        # folds straight into its register; transposing it as well could push it below 30 Hz.
        if random.random() < 0.55:
            layers.append(_sub_under(bass))
        return layers

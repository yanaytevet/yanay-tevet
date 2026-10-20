import random
import uuid
from collections.abc import Iterable
from typing import Any

from genre_trainer.enums.genre_type import GenreType

_N = None


def _cfg(id_: str, role: str, vol: float, note_dur: str, inst_type: str, inst_opts: dict,
         effects: list, steps: list, velocities: list | None = None,
         entry_loop: int = 0, dropout_prob: float = 0.0,
         automation: list | None = None,
         loop_modulo: int = 0, loop_modulo_remainder: int = 0,
         pan: float | None = None, slides: list[bool] | None = None,
         subdivision: str = '16n', sidechain: str | None = None) -> dict[str, Any]:
    pattern: dict = {'subdivision': subdivision, 'steps': steps}
    if velocities is not None:
        pattern['velocities'] = velocities
    if slides is not None:
        pattern['slides'] = slides
    result: dict[str, Any] = {
        'id': id_,
        'role': role,
        'volume': vol,
        'note_duration': note_dur,
        'instrument': {'type': inst_type, 'options': inst_opts},
        'effects': effects,
        'pattern': pattern,
    }
    if entry_loop:
        result['entry_loop'] = entry_loop
    if dropout_prob:
        result['dropout_prob'] = dropout_prob
    if automation:
        result['automation'] = automation
    if loop_modulo:
        result['loop_modulo'] = loop_modulo
        result['loop_modulo_remainder'] = loop_modulo_remainder
    if pan is not None:
        result['pan'] = pan
    if sidechain is not None:
        result['sidechain'] = sidechain
    return result


def _auto(target: str, from_val: float, to_val: float, waveform: str = 'tri') -> dict:
    """Parameter automation: target is 'effect:N:paramName'."""
    return {'target': target, 'from_val': from_val, 'to_val': to_val, 'waveform': waveform}


def _vel(steps: list, accent_prob: float = 0.2, ghost_prob: float = 0.12) -> list[float | None]:
    vels = []
    for step in steps:
        if step is None:
            vels.append(None)
        elif random.random() < ghost_prob:
            vels.append(round(random.uniform(0.2, 0.38), 2))
        elif random.random() < accent_prob:
            vels.append(round(random.uniform(0.85, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.5, 0.78), 2))
    return vels


def _vel_groove(steps: list) -> list[float | None]:
    """Quarter-note accents, medium 8ths, quiet 16th offbeats."""
    vels = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
            continue
        pos = i % 32
        if pos % 4 == 0:
            vels.append(round(random.uniform(0.75, 0.95), 2))
        elif pos % 2 == 0:
            vels.append(round(random.uniform(0.45, 0.65), 2))
        else:
            vels.append(round(random.uniform(0.2, 0.4), 2))
    return vels


def _vel_kick(steps: list) -> list[float | None]:
    """Every beat equally strong, softer pickups between beats. Weaker kicks on 2 and 4 would read as
    half-time against a four-on-the-floor pattern."""
    vels = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        elif i % 4 == 0:
            vels.append(round(random.uniform(0.9, 1.0), 2))
        else:
            vels.append(round(random.uniform(0.7, 0.85), 2))
    return vels


def _vel_snare(steps: list) -> list[float | None]:
    """High velocity on beats 2 & 4, ghost level on all others."""
    vels = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
            continue
        pos = i % 32
        if pos in {4, 12, 20, 28}:
            vels.append(round(random.uniform(0.78, 0.95), 2))
        else:
            vels.append(round(random.uniform(0.16, 0.32), 2))
    return vels



def _vel_flat(steps: list, low: float, high: float) -> list[float | None]:
    """Machine-even velocities in [low, high] — psy basses and hats get no ghosts or accents."""
    return [None if s is None else round(random.uniform(low, high), 2) for s in steps]


def _vel_roll(steps: list, levels: dict[int, tuple[float, float]],
              default: tuple[float, float]) -> list[float | None]:
    """Velocities by position inside the beat (i % 4 -> (low, high)). A rolling bass sets the 16th
    straight after the kick back, under the kick's tail, and lets the middle one lead."""
    return [None if s is None else round(random.uniform(*levels.get(i % 4, default)), 2)
            for i, s in enumerate(steps)]


def _vel_rumble(steps: list) -> list[float | None]:
    """The techno rumble swells out of each kick: the 16th straight after the kick sits lowest, the
    offbeat peaks and the last 16th eases off into the next kick."""
    ranges = {0: (0.7, 0.8), 1: (0.6, 0.72), 2: (0.84, 0.96), 3: (0.7, 0.82)}
    vels = []
    for i, step in enumerate(steps):
        if step is None:
            vels.append(None)
        else:
            low, high = ranges[i % 4]
            vels.append(round(random.uniform(low, high), 2))
    return vels


# ---------------------------------------------------------------------------
# PATTERN BUILDERS — patterns are written as hit positions or per-beat notes
# rather than 32-slot lists, so the comment grid above each pool entry is the
# thing to read and the core rhythm can't drift between entries.
# ---------------------------------------------------------------------------
def _on(positions: Iterable[int], note: str = 'C2', length: int = 32) -> list[str | None]:
    """`note` on the given steps, rests everywhere else."""
    hits = set(positions)
    return [note if i in hits else _N for i in range(length)]


def _at(notes: dict[int, str], length: int = 32) -> list[str | None]:
    """A melodic step list from {step: note}. Held lines are mostly rests, so writing only where the
    notes start shows the phrasing far better than a 32-slot list."""
    return [notes.get(i) for i in range(length)]


def _four(note: str) -> list[str | None]:
    """Strict four-on-the-floor: one kick on every quarter, nothing in between."""
    return [note, _N, _N, _N] * 8


def _roll(*beats: str) -> list[str | None]:
    """The rolling psy bassline (K-B-B-B), one beat at a time: each beat's first 16th belongs to the
    kick and stays silent, the three notes given ('A1 A1 Bb1') fill the rest. '-' rests a 16th."""
    steps: list[str | None] = []
    for beat in beats:
        steps.append(_N)
        steps.extend(_N if note == '-' else note for note in beat.split())
    return steps


def _rolling(root: str, changes: dict[int, str | None] | None = None) -> list[str | None]:
    """K-B-B-B on one root over both bars: the bass fills the three 16ths after every kick and is never
    on the kick itself. `changes` swaps single steps for the passing notes, octave jumps and dropped
    notes of a phrase-end fill."""
    steps = _on((i for i in range(32) if i % 4 != 0), root)
    for i, note in (changes or {}).items():
        steps[i] = note
    return steps


def _phrase(length: int, *placed: tuple[int, str]) -> list[str | None]:
    """A mostly silent pattern of `length` steps holding short fragments, each given as
    (start step, 'notes ...'); '-' rests a step inside a fragment."""
    steps: list[str | None] = [_N] * length
    for start, notes in placed:
        for offset, note in enumerate(notes.split()):
            steps[start + offset] = _N if note == '-' else note
    return steps


def _clear_kick_steps(layer: dict[str, Any], kick: dict[str, Any]) -> None:
    """Carve a bass out wherever the kick hits, so a kick entry with an extra 16th lead-in never
    lands on top of a bass note. Call before velocities and slides are assigned."""
    kick_hits = {i for i, step in enumerate(kick['pattern']['steps']) if step is not None}
    layer['pattern']['steps'] = [
        _N if i in kick_hits else step for i, step in enumerate(layer['pattern']['steps'])
    ]


def _tune_kick(kick: dict[str, Any], root_pc: int, lowest_midi: int) -> None:
    """Tune the kick to the track's root. Its tail (and a rumble built from it) then agrees with the
    bassline instead of beating against it — on a distorted kick the tail is a clearly pitched note.
    The kick lands in the 12 semitones from lowest_midi up."""
    note = _midi_to_note(lowest_midi + (root_pc - lowest_midi) % 12)
    kick['pattern']['steps'] = [note if step is not None else _N for step in kick['pattern']['steps']]

def _dist(d: float, wet: float) -> dict:
    return {'type': 'Distortion', 'options': {'distortion': d}, 'wet': wet}


def _reverb(decay: float, wet: float, pre: float | None = None) -> dict:
    opts: dict = {'decay': decay}
    if pre is not None:
        opts['preDelay'] = pre
    return {'type': 'Reverb', 'options': opts, 'wet': wet}


def _delay(t: str, fb: float, wet: float) -> dict:
    return {'type': 'FeedbackDelay', 'options': {'delayTime': t, 'feedback': fb}, 'wet': wet}


def _filt(ftype: str, freq: float, q: float, wet: float = 1.0) -> dict:
    return {'type': 'Filter', 'options': {'type': ftype, 'frequency': freq, 'Q': q}, 'wet': wet}


def _chorus(f: float, dt: float, depth: float, wet: float) -> dict:
    return {'type': 'Chorus', 'options': {'frequency': f, 'delayTime': dt, 'depth': depth}, 'wet': wet}


def _wobble(rate: str, base_freq: float, octaves: float, q: float, wet: float = 1.0,
            shape: str = 'sine') -> dict:
    """Tempo-synced filter LFO (Tone.AutoFilter) — the wobble of bass music. `rate` is a note
    value ('8n', '8t', '16n'), so the wobble stays locked to the beat."""
    return {'type': 'AutoFilter',
            'options': {'frequency': rate, 'baseFrequency': base_freq, 'octaves': octaves, 'type': shape,
                        'filter': {'type': 'lowpass', 'Q': q, 'rolloff': -24}},
            'wet': wet}


def _pingpong(t: str, fb: float, wet: float) -> dict:
    return {'type': 'PingPongDelay', 'options': {'delayTime': t, 'feedback': fb}, 'wet': wet}


def _slides(steps: list, prob: float = 0.25) -> list[bool]:
    """303-style slides: a slide step glides from the previous note instead of retriggering, so it
    is only marked on a note that directly follows another note (wrapping at the loop end)."""
    return [
        step is not None and steps[i - 1] is not None and random.random() < prob
        for i, step in enumerate(steps)
    ]


# ---------------------------------------------------------------------------
# KEY COHERENCE
#
# Every melodic layer pool is hand-written in its own key (the bass pool might
# hold A-minor, E-minor and D-minor lines; the lead pool E-Phrygian, etc.).
# Layers are picked independently, so without correction a track can stack an
# A-minor bass under a G-rooted stab over a C pad — three different roots at
# once, which reads instantly as "out of tune / cheap".
#
# _apply_key_coherence picks one root for the whole track and transposes every
# melodic-role layer so its own root lands on that shared root. Internal
# intervals (and therefore each pattern's mode/character) are preserved; only
# the absolute pitch moves, by at most a tritone so registers stay put.
# Percussion roles (kick/snare/hihat/perc) are left untouched — their note
# names are just triggers for noise/metal voices, not musical pitches.
# ---------------------------------------------------------------------------
_MELODIC_ROLES = frozenset({'bass', 'sub', 'lead', 'stab', 'pad'})

_PC_BY_LETTER = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_NAME_BY_PC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Common minor-friendly dance roots (pitch classes): A C D E F G B F# Bb Eb.
_TRACK_ROOT_PCS = [9, 0, 2, 4, 5, 7, 11, 6, 10, 3]


def _note_to_midi(note: str) -> int:
    pc = _PC_BY_LETTER[note[0].upper()]
    i = 1
    while i < len(note) and note[i] in ('#', 'b'):
        pc += 1 if note[i] == '#' else -1
        i += 1
    octave = int(note[i:])
    return (octave + 1) * 12 + pc


def _midi_to_note(midi: int) -> str:
    return f'{_NAME_BY_PC[midi % 12]}{midi // 12 - 1}'


def _transpose_step(step: str | None, shift: int) -> str | None:
    """Shift a step (single note or comma-separated chord) by `shift` semitones."""
    if step is None or shift == 0:
        return step
    return ','.join(_midi_to_note(_note_to_midi(n) + shift) for n in step.split(','))


def _detect_root_pc(steps: list) -> int | None:
    """Root pitch class of a pattern: the most common primary pitch (for chords,
    the first/lowest note of each step), tie-broken toward the first hit."""
    primaries = [_note_to_midi(s.split(',')[0]) % 12 for s in steps if s is not None]
    if not primaries:
        return None
    counts: dict[int, int] = {}
    for pc in primaries:
        counts[pc] = counts.get(pc, 0) + 1
    return max(counts, key=lambda pc: (counts[pc], pc == primaries[0]))


def _transpose_layer_to_root(layer: dict[str, Any], target_pc: int) -> None:
    steps = layer['pattern']['steps']
    root = _detect_root_pc(steps)
    if root is None:
        return
    shift = (target_pc - root) % 12
    if shift > 6:
        shift -= 12  # keep movement within a tritone so registers don't jump an octave
    if shift == 0:
        return
    layer['pattern']['steps'] = [_transpose_step(s, shift) for s in steps]


# ---------------------------------------------------------------------------
# KICK ENHANCEMENT
#
# Every genre's kick was a bare MembraneSynth thump — near-identical across
# genres and lacking attack definition, which is exactly why the kick-defined
# genres (techno / tek / hard-techno) were hard to tell apart. _enhance_kick
# adds a short, bright "click transient" layer locked to the kick hits (the
# part the ear reads as punch/attack) and, for kick-defined genres, a
# saturating distortion. Click brightness/level and saturation are chosen per
# profile so the kick itself becomes a genre cue: hard genres click bright and
# distort; deep/house kicks stay round and soft.
# ---------------------------------------------------------------------------
_KICK_PROFILES = {
    GenreType.TEK: 'hard',
    GenreType.HARD_TECHNO: 'hard',
    GenreType.DARK_PSY: 'hard',
    GenreType.MELODIC_TECHNO: 'deep',
    GenreType.MINIMAL_TECHNO: 'deep',
    GenreType.HOUSE: 'deep',
}  # everything else falls back to 'punchy'

# profile -> (MetalSynth frequency, click volume dB, decay seconds)
_KICK_CLICK_PARAMS = {
    'hard': (820, -9, 0.018),
    'punchy': (620, -13, 0.022),
    'deep': (380, -17, 0.028),
}


def _build_kick_click(kick_steps: list, profile: str) -> dict[str, Any]:
    freq, vol, decay = _KICK_CLICK_PARAMS[profile]
    steps = ['C5' if s is not None else None for s in kick_steps]
    return _cfg('kick_click', 'kick', vol, '32n', 'MetalSynth',
                {'frequency': freq, 'envelope': {'attack': 0.001, 'decay': decay, 'release': 0.005},
                 'harmonicity': 3.2, 'modulationIndex': 16, 'resonance': 7000, 'octaves': 1.0},
                [], steps)


class BaseTrackGenerator:
    GENRE: GenreType
    BPM_RANGE: tuple[int, int]
    # Transport-level 16n swing amount. Genres override this where shuffle is part of the feel
    # (house ~0.12, garage ~0.2, jungle/DnB ~0.05 light); most four-on-the-floor genres stay at 0.
    SWING: float = 0.0
    # The parts that define the genre, most telling first. The reveal highlights the first of these
    # roles the track actually has, so the listener knows which layer to solo.
    KEY_ROLES: tuple[str, ...] = ('bass',)
    # The player ducks the non-kick layers on every hit of the main kick. Depth scales the per-role
    # duck (0 turns it off, 1 is the default pump); release is how long the duck takes to recover, in
    # beats. Pumping genres (house, trance-y techno) recover slowly; psy recovers within a 16th so the
    # rolling bass between kicks stays at full level.
    SIDECHAIN_DEPTH: float = 1.0
    SIDECHAIN_RELEASE: float = 0.5
    # Output trim in dB, applied after the player's limiter, so every genre plays at about the same
    # loudness (−18 dB RMS, the quietest genres' level). Without it the loudest genres sat 10 dB above
    # the quietest — loudness became a giveaway — and they peaked at full scale. Cut only: a boost after
    # the limiter would push peaks past it. Measured by rendering tracks offline; re-measure after
    # changing a genre's levels (docs/genre-trainer.md).
    LEVEL_DB: float = 0.0

    @classmethod
    def generate(cls) -> dict[str, Any]:
        layers = cls._generate_layers()
        cls._enhance_kick(layers)
        roles = {layer['role'] for layer in layers}
        return {
            'id': f'{cls.GENRE.value}_{uuid.uuid4().hex[:6]}',
            'genre': cls.GENRE.value,
            'bpm': random.randint(*cls.BPM_RANGE),
            'swing': cls.SWING,
            'sidechain_depth': cls.SIDECHAIN_DEPTH,
            'sidechain_release': cls.SIDECHAIN_RELEASE,
            'gain_db': cls.LEVEL_DB,
            'key_role': next((role for role in cls.KEY_ROLES if role in roles), None),
            'layers': layers,
        }

    @classmethod
    def _generate_layers(cls) -> list[dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    def _enhance_kick(cls, layers: list[dict[str, Any]]) -> None:
        """Give the kick attack definition and a genre-specific character. Adds a
        click-transient layer locked to the kick hits, plus saturation for the
        kick-defined ('hard') genres. The extra distortion is appended last so it
        never shifts existing effect indices (automation targets stay valid)."""
        profile = _KICK_PROFILES.get(cls.GENRE, 'punchy')
        kick = next((layer for layer in layers if layer['role'] == 'kick'), None)
        if kick is None:
            return
        if profile == 'hard' and not any(e['type'] == 'Distortion' for e in kick['effects']):
            kick['effects'].append(_dist(0.35, 0.45))
        click = _build_kick_click(kick['pattern']['steps'], profile)
        click['pattern']['velocities'] = _vel_kick(click['pattern']['steps'])
        layers.append(click)

    @classmethod
    def _pick(cls, pool: list[dict[str, Any]]) -> dict[str, Any]:
        return random.choice(pool)

    @classmethod
    def _maybe(cls, pool: list[dict[str, Any]], probability: float = 0.6) -> dict[str, Any] | None:
        if random.random() < probability:
            return random.choice(pool)
        return None

    @classmethod
    def _apply_key_coherence(cls, layers: list[dict[str, Any]], root_pc: int | None = None) -> int:
        """Transpose every melodic-role layer onto one shared root so the track is
        in a single key. Returns the chosen root pitch class. Call once at the end
        of _generate_layers, after all layers (and their velocities) are assembled."""
        if root_pc is None:
            root_pc = random.choice(_TRACK_ROOT_PCS)
        for layer in layers:
            if layer['role'] in _MELODIC_ROLES:
                _transpose_layer_to_root(layer, root_pc)
        return root_pc

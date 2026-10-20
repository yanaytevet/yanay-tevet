import random

from django.test import SimpleTestCase

from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import _MELODIC_ROLES, _detect_root_pc, _note_to_midi
from genre_trainer.generators.genre_generator_registry import GENRE_GENERATORS
from genre_trainer.views.get_random_track_view import TrackSchema

# Each generator picks from pools at random, so every rule is checked over many draws.
_RUNS = 60

_PSY = frozenset({
    GenreType.PSYTRANCE, GenreType.PROGRESSIVE_PSY, GenreType.GOA, GenreType.DARK_PSY,
    GenreType.HIGHTEK, GenreType.WEIRD_FINNISH_TRANCE,
})
_FOUR_ON_THE_FLOOR = _PSY | {
    GenreType.TECHNO, GenreType.HARD_TECHNO, GenreType.ACID_TECHNO, GenreType.MINIMAL_TECHNO,
    GenreType.MELODIC_TECHNO, GenreType.TEK, GenreType.HOUSE,
}
# A 303 line runs straight across the kick; that is the sound of acid, not a collision.
_BASS_MAY_HIT_KICK = frozenset({GenreType.ACID_TECHNO})
_BACKBEAT = frozenset({GenreType.DRUM_AND_BASS, GenreType.JUNGLE})

_STEPS_PER_LOOP = {'16n': 32, '32n': 64}
_QUARTERS = frozenset(range(0, 32, 4))
_BACKBEAT_STEPS = frozenset({4, 12, 20, 28})
_ROLES = frozenset({'kick', 'sub', 'bass', 'snare', 'hihat', 'perc', 'lead', 'stab', 'pad'})
_SIDECHAIN = frozenset({'deep', 'medium', 'shallow', 'none'})
_TRAITS = frozenset({'drums', 'bass', 'signature', 'mood'})


def _hits(layer: dict) -> set[int]:
    return {i for i, step in enumerate(layer['pattern']['steps']) if step is not None}


def _main_kick(track: dict) -> dict:
    return next(layer for layer in track['layers'] if layer['id'] == 'kick')


class GeneratorTestCase(SimpleTestCase):
    def setUp(self) -> None:
        random.seed(7)

    def tracks(self, genre: GenreType):
        generator = GENRE_GENERATORS[genre]
        for _ in range(_RUNS):
            yield generator.generate()


class EveryGenreTest(GeneratorTestCase):
    def test_every_genre_has_a_generator(self) -> None:
        self.assertEqual(set(GENRE_GENERATORS), set(GenreType))

    def test_tracks_are_well_formed(self) -> None:
        for genre in GenreType:
            for track in self.tracks(genre):
                with self.subTest(genre=genre.value):
                    TrackSchema.model_validate(track)
                    self.assertEqual(track['genre'], genre.value)
                    self.assertIsNotNone(track['key_role'], 'the reveal needs a part to point at')
                    self.assertGreaterEqual(track['sidechain_depth'], 0)
                    self.assertGreater(track['sidechain_release'], 0)
                    self.assertTrue(any(layer['id'] == 'kick' for layer in track['layers']),
                                    'the sidechain duck is triggered by the layer with id "kick"')
                    for layer in track['layers']:
                        self.assert_layer_well_formed(layer)

    def assert_layer_well_formed(self, layer: dict) -> None:
        pattern = layer['pattern']
        steps = pattern['steps']
        self.assertIn(layer['role'], _ROLES)
        self.assertEqual(len(steps), _STEPS_PER_LOOP[pattern['subdivision']], layer['id'])
        if layer.get('sidechain') is not None:
            self.assertIn(layer['sidechain'], _SIDECHAIN)
        if pattern.get('velocities') is not None:
            self.assertEqual(len(pattern['velocities']), len(steps), layer['id'])
        slides = pattern.get('slides')
        if slides is not None:
            self.assertEqual(len(slides), len(steps), layer['id'])
            for i, slide in enumerate(slides):
                if slide:
                    self.assertIsNotNone(steps[i], f'{layer["id"]}: slide on a rest')
                    self.assertIsNotNone(steps[i - 1], f'{layer["id"]}: slide with no note to glide from')
        if layer['role'] not in {'kick', 'snare', 'hihat', 'perc'}:
            for step in steps:
                if step is not None:
                    for note in step.split(','):
                        _note_to_midi(note)


class RhythmGrammarTest(GeneratorTestCase):
    """The few rhythmic rules that make each genre recognisable at all. A pattern that breaks one of
    these trains the ear on the wrong cue."""

    def test_four_on_the_floor_kicks_land_on_every_beat(self) -> None:
        for genre in _FOUR_ON_THE_FLOOR:
            for track in self.tracks(genre):
                with self.subTest(genre=genre.value):
                    self.assertTrue(_QUARTERS <= _hits(_main_kick(track)))

    def test_psy_kicks_are_strictly_four_on_the_floor(self) -> None:
        for genre in _PSY:
            for track in self.tracks(genre):
                with self.subTest(genre=genre.value):
                    self.assertEqual(_hits(_main_kick(track)), set(_QUARTERS))

    def test_bass_stays_off_the_kick(self) -> None:
        for genre in _FOUR_ON_THE_FLOOR - _BASS_MAY_HIT_KICK:
            for track in self.tracks(genre):
                kicks = _hits(_main_kick(track))
                for layer in track['layers']:
                    if layer['role'] in {'bass', 'sub'}:
                        with self.subTest(genre=genre.value, layer=layer['id']):
                            self.assertFalse(_hits(layer) & kicks)

    def test_no_sustained_sub_under_a_psy_kick(self) -> None:
        for genre in _PSY | {GenreType.HARD_TECHNO}:
            for track in self.tracks(genre):
                with self.subTest(genre=genre.value):
                    self.assertFalse(any(layer['role'] == 'sub' for layer in track['layers']))

    def test_breakbeats_keep_the_backbeat(self) -> None:
        for genre in _BACKBEAT:
            for track in self.tracks(genre):
                snare = next(layer for layer in track['layers'] if layer['id'] == 'snare')
                with self.subTest(genre=genre.value):
                    self.assertTrue(_BACKBEAT_STEPS <= _hits(snare))

    def test_breakbeat_kicks_are_not_four_on_the_floor(self) -> None:
        for genre in _BACKBEAT | {GenreType.PSY_BASS}:
            for track in self.tracks(genre):
                with self.subTest(genre=genre.value):
                    self.assertFalse(_QUARTERS <= _hits(_main_kick(track)))

    def test_acid_lines_slide(self) -> None:
        slid = 0
        for track in self.tracks(GenreType.ACID_TECHNO):
            bass = next(layer for layer in track['layers'] if layer['role'] == 'bass')
            slid += any(bass['pattern'].get('slides') or [])
        self.assertGreater(slid, _RUNS * 0.8)


class ProfileAndKeyTest(GeneratorTestCase):
    def test_every_genre_has_a_profile(self) -> None:
        for genre, generator in GENRE_GENERATORS.items():
            with self.subTest(genre=genre.value):
                profile = generator.PROFILE
                self.assertIn(profile.key_trait, _TRAITS)
                for text in (profile.drums, profile.bass, profile.signature, profile.mood):
                    self.assertTrue(text.strip())

    def test_a_requested_root_puts_every_melodic_part_in_that_key(self) -> None:
        """The comparison track is generated in the key of the track it is played against; a part
        left in another key would make the switch sound like a key change, not a genre change."""
        for genre, generator in GENRE_GENERATORS.items():
            for root in range(12):
                track = generator.generate(root)
                with self.subTest(genre=genre.value, root=root):
                    self.assertEqual(track['root'], root)
                    for layer in track['layers']:
                        if layer['role'] in _MELODIC_ROLES:
                            self.assertEqual(_detect_root_pc(layer['pattern']['steps']), root, layer['id'])

    def test_without_a_request_the_track_reports_its_key(self) -> None:
        for genre, generator in GENRE_GENERATORS.items():
            with self.subTest(genre=genre.value):
                self.assertIn(generator.generate()['root'], range(12))

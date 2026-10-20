import random
from typing import Any

from genre_trainer.generators.genre_generator_registry import GENRE_GENERATORS


class GenreCatalogManager:
    @staticmethod
    def list_profiles() -> list[dict[str, Any]]:
        """Every genre's listening profile, with its tempo range taken from the generator itself."""
        return [
            {
                'genre': genre_type.value,
                'bpm_min': generator.BPM_RANGE[0],
                'bpm_max': generator.BPM_RANGE[1],
                'drums': generator.PROFILE.drums,
                'bass': generator.PROFILE.bass,
                'signature': generator.PROFILE.signature,
                'mood': generator.PROFILE.mood,
                'key_trait': generator.PROFILE.key_trait,
                'kick_pattern': generator.PROFILE.kick_pattern,
                'bass_pattern': generator.PROFILE.bass_pattern,
            }
            for genre_type, generator in GENRE_GENERATORS.items()
        ]

    @staticmethod
    def generate_random_track(genres: set[str], root_pc: int | None) -> dict[str, Any]:
        """A track of one of `genres` (any genre when none of them is known), in the key of `root_pc`
        when one is given."""
        available = {
            genre_type: generator
            for genre_type, generator in GENRE_GENERATORS.items()
            if genre_type.value in genres
        } or dict(GENRE_GENERATORS)
        genre_type = random.choice(list(available.keys()))
        return available[genre_type].generate(root_pc)

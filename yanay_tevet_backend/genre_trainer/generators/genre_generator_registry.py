from genre_trainer.enums.genre_type import GenreType
from genre_trainer.generators.base_track_generator import BaseTrackGenerator
from genre_trainer.generators.acid_techno_generator import AcidTechnoTrackGenerator
from genre_trainer.generators.dark_psy_generator import DarkPsyTrackGenerator
from genre_trainer.generators.drum_and_bass_generator import DrumAndBassTrackGenerator
from genre_trainer.generators.forest_psy_generator import ForestPsyTrackGenerator
from genre_trainer.generators.goa_generator import GoaTrackGenerator
from genre_trainer.generators.hard_techno_generator import HardTechnoTrackGenerator
from genre_trainer.generators.hightek_generator import HightekTrackGenerator
from genre_trainer.generators.house_generator import HouseTrackGenerator
from genre_trainer.generators.jungle_generator import JungleTrackGenerator
from genre_trainer.generators.melodic_techno_generator import MelodicTechnoTrackGenerator
from genre_trainer.generators.minimal_techno_generator import MinimalTechnoTrackGenerator
from genre_trainer.generators.psy_bass_generator import PsyBassTrackGenerator
from genre_trainer.generators.psytrance_generator import PsytranceTrackGenerator
from genre_trainer.generators.techno_generator import TechnoTrackGenerator
from genre_trainer.generators.tek_generator import TekTrackGenerator
from genre_trainer.generators.weird_finnish_trance_generator import WeirdFinnishTranceTrackGenerator

GENRE_GENERATORS: dict[GenreType, type[BaseTrackGenerator]] = {
    GenreType.ACID_TECHNO: AcidTechnoTrackGenerator,
    GenreType.DARK_PSY: DarkPsyTrackGenerator,
    GenreType.DRUM_AND_BASS: DrumAndBassTrackGenerator,
    GenreType.FOREST_PSY: ForestPsyTrackGenerator,
    GenreType.GOA: GoaTrackGenerator,
    GenreType.HARD_TECHNO: HardTechnoTrackGenerator,
    GenreType.HIGHTEK: HightekTrackGenerator,
    GenreType.HOUSE: HouseTrackGenerator,
    GenreType.JUNGLE: JungleTrackGenerator,
    GenreType.MELODIC_TECHNO: MelodicTechnoTrackGenerator,
    GenreType.MINIMAL_TECHNO: MinimalTechnoTrackGenerator,
    GenreType.PSY_BASS: PsyBassTrackGenerator,
    GenreType.PSYTRANCE: PsytranceTrackGenerator,
    GenreType.TECHNO: TechnoTrackGenerator,
    GenreType.TEK: TekTrackGenerator,
    GenreType.WEIRD_FINNISH_TRANCE: WeirdFinnishTranceTrackGenerator,
}

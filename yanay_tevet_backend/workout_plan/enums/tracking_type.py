from common.base_enum import BaseEnum


class TrackingType(BaseEnum):
    """What a set of an exercise records. Fixed so every exercise has one obvious progress metric."""

    REPS = 'reps'
    WEIGHT_REPS = 'weight_reps'
    TIME = 'time'
    DISTANCE = 'distance'
    LAPS = 'laps'

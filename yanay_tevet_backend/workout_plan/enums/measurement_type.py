from common.base_enum import BaseEnum


# Used only by migration 0001 (the first version of this app); kept so that migration still imports.
class MeasurementType(BaseEnum):
    REPS = 'reps'
    TIME = 'time'

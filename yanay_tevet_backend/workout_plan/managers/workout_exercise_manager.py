from django.db.models import Max

from users.models import User
from workout_plan.enums.measurement_type import MeasurementType
from workout_plan.models.exercise_set import ExerciseSet
from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.serializers.workout_exercise_serializers.workout_exercise_serializer import (
    ExerciseSetWritableSchema,
    WorkoutExerciseWritableSchema,
)


class WorkoutExerciseManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_exercise(self, routine_id: int, writable: WorkoutExerciseWritableSchema) -> WorkoutExercise:
        measurement_type = writable.measurement_type or MeasurementType.REPS
        next_order = await self._next_order(routine_id)
        exercise = WorkoutExercise(
            routine_id=routine_id,
            name=(writable.name or '').strip(),
            measurement_type=measurement_type,
            notes=(writable.notes or '').strip(),
            order=next_order,
        )
        await exercise.asave()
        if writable.sets is not None:
            await self._replace_sets(exercise, writable.sets, measurement_type)
        return exercise

    async def update_exercise(self, exercise: WorkoutExercise, writable: WorkoutExerciseWritableSchema) -> None:
        fields = writable.model_dump(exclude_unset=True)
        if 'name' in fields and writable.name is not None:
            exercise.name = writable.name.strip()
        if 'notes' in fields and writable.notes is not None:
            exercise.notes = writable.notes.strip()
        if 'measurement_type' in fields and writable.measurement_type is not None:
            exercise.measurement_type = writable.measurement_type
        await exercise.asave()
        if 'sets' in fields and writable.sets is not None:
            await self._replace_sets(exercise, writable.sets, MeasurementType(exercise.measurement_type))

    async def _replace_sets(
        self,
        exercise: WorkoutExercise,
        sets: list[ExerciseSetWritableSchema],
        measurement_type: MeasurementType,
    ) -> None:
        await ExerciseSet.objects.filter(exercise_id=exercise.id).adelete()
        new_sets = [
            ExerciseSet(
                exercise_id=exercise.id,
                order=index,
                reps=set_data.reps if measurement_type == MeasurementType.REPS else None,
                duration_seconds=set_data.duration_seconds if measurement_type == MeasurementType.TIME else None,
            )
            for index, set_data in enumerate(sets)
        ]
        if new_sets:
            await ExerciseSet.objects.abulk_create(new_sets)

    async def _next_order(self, routine_id: int) -> int:
        aggregate = await WorkoutExercise.objects.filter(routine_id=routine_id).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1

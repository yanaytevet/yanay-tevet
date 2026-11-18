# Workout plan

A gym-and-cardio tracker (`workout_plan` backend app, `src/app/workout-plan/`). Gated by the `workout_plan`
permission; sharing a plan grants it.

- **Plans → days → exercises.** A plan has day types (Day A, Day B…) plus one *every-day* section
  (`PlanDay.is_every_day`, one per plan by a constraint), shown first on every day. A `PlanExercise` is an
  exercise on a day with its targets (sets, reps, kg, seconds, km, laps), rest seconds and notes. A missing
  `target_reps` means "as many as possible".
- **Exercise library.** `Exercise` rows with `owner=None` are the built-in catalog, seeded by migration 0003 from
  `workout_plan/catalog/exercise_catalog.py` (English + Hebrew names, keyed by a permanent `catalog_key`).
  To add catalog entries, append to that list and add a new data migration that runs the same seed. Users add
  their own (`owner` set); a collaborator's custom exercise becomes visible once it is in a shared plan.
- **Tracking type is fixed per exercise** (`reps`, `weight_reps`, `time`, `distance`, `laps`) plus `per_side`
  (left/right logged separately). It decides the inputs, the progress metric and the graph, and cannot change
  once the exercise has logged sets.
- **Logs are personal.** A `WorkoutSession` belongs to one user even on a shared plan; it snapshots plan/day
  names and the pool length so history survives plan edits. `SetLog` is one done set; logging the same
  (exercise, entry, set number, side) again updates it. Starting a day again within 6 hours resumes the
  unfinished session.
- **Progress** (`WorkoutProgressManager`): per session, the heaviest set (per side too) and volume for weights,
  best/total reps, longest/total time, distance and pace. The frontend draws it with its own SVG chart
  (`progress/progress-chart/`), no chart library.
- **Language.** The app's strings are in `workout-plan/i18n/`, in every site
  language (`docs/frontend.md`, *Language*); its in-app switches change that site setting. Exercise names come
  from the `exerciseName` pipe: built-in exercises have every language (`name_translations`, seeded from
  `catalog/exercise_name_translations.py`); a user's own exercise only has the English/Hebrew names typed in.
- **Claude** builds and edits plans and reads progress through `mcp/tools/workout_plan_tools.py`; it does not log
  workouts. `create_workout_plan` validates every exercise id before writing anything.
- `workout_plan/enums/measurement_type.py` is dead code kept only because migration 0001 imports it.

from workout_plan.permissions_checkers.workout_plan_permission_checker import WorkoutPlanPermissionChecker
from workout_plan.views.exercise_views.create_workout_exercise_view import CreateWorkoutExerciseView
from workout_plan.views.exercise_views.delete_workout_exercise_view import DeleteWorkoutExerciseView
from workout_plan.views.exercise_views.get_workout_exercise_view import GetWorkoutExerciseView
from workout_plan.views.exercise_views.paginate_workout_exercises_view import PaginateWorkoutExercisesView
from workout_plan.views.exercise_views.update_workout_exercise_view import UpdateWorkoutExerciseView
from workout_plan.views.routine_views.create_workout_routine_view import CreateWorkoutRoutineView
from workout_plan.views.routine_views.delete_workout_routine_view import DeleteWorkoutRoutineView
from workout_plan.views.routine_views.get_workout_routine_view import GetWorkoutRoutineView
from workout_plan.views.routine_views.paginate_workout_routines_view import PaginateWorkoutRoutinesView
from workout_plan.views.routine_views.update_workout_routine_view import UpdateWorkoutRoutineView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('workout-plan', WorkoutPlanPermissionChecker())

# --- Routines ---
PaginateWorkoutRoutinesView.register_get(router, 'routines/')
CreateWorkoutRoutineView.register_post(router, 'routines/')
GetWorkoutRoutineView.register_get(router, 'routines/{int:object_id}/')
UpdateWorkoutRoutineView.register_patch_by_id(router, prefix='routines')
DeleteWorkoutRoutineView.register_delete_by_id(router, prefix='routines')

# --- Exercises ---
PaginateWorkoutExercisesView.register_get(router, 'routines/{int:routine_id}/exercises/')
CreateWorkoutExerciseView.register_post(router, 'exercises/')
GetWorkoutExerciseView.register_get(router, 'exercises/{int:object_id}/')
UpdateWorkoutExerciseView.register_patch_by_id(router, prefix='exercises')
DeleteWorkoutExerciseView.register_delete_by_id(router, prefix='exercises')

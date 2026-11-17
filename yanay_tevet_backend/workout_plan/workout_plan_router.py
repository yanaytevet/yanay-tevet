from common.django_utils.api_router_creator import ApiRouterCreator
from workout_plan.permissions_checkers.workout_plan_permission_checker import WorkoutPlanPermissionChecker
from workout_plan.views.day_views.create_plan_day_view import CreatePlanDayView
from workout_plan.views.day_views.delete_plan_day_view import DeletePlanDayView
from workout_plan.views.day_views.reorder_plan_days_view import ReorderPlanDaysView
from workout_plan.views.day_views.update_plan_day_view import UpdatePlanDayView
from workout_plan.views.exercise_views.create_exercise_view import CreateExerciseView
from workout_plan.views.exercise_views.delete_exercise_view import DeleteExerciseView
from workout_plan.views.exercise_views.list_exercises_view import ListExercisesView
from workout_plan.views.exercise_views.update_exercise_view import UpdateExerciseView
from workout_plan.views.plan_exercise_views.create_plan_exercise_view import CreatePlanExerciseView
from workout_plan.views.plan_exercise_views.delete_plan_exercise_view import DeletePlanExerciseView
from workout_plan.views.plan_exercise_views.reorder_plan_exercises_view import ReorderPlanExercisesView
from workout_plan.views.plan_exercise_views.update_plan_exercise_view import UpdatePlanExerciseView
from workout_plan.views.plan_views.create_workout_plan_view import CreateWorkoutPlanView
from workout_plan.views.plan_views.delete_workout_plan_view import DeleteWorkoutPlanView
from workout_plan.views.plan_views.get_workout_plan_view import GetWorkoutPlanView
from workout_plan.views.plan_views.list_workout_plan_members_view import ListWorkoutPlanMembersView
from workout_plan.views.plan_views.paginate_workout_plans_view import PaginateWorkoutPlansView
from workout_plan.views.plan_views.share_workout_plan_view import ShareWorkoutPlanView
from workout_plan.views.plan_views.unshare_workout_plan_view import UnshareWorkoutPlanView
from workout_plan.views.plan_views.update_workout_plan_view import UpdateWorkoutPlanView
from workout_plan.views.preferences_views.get_workout_preferences_view import GetWorkoutPreferencesView
from workout_plan.views.preferences_views.update_workout_preferences_view import UpdateWorkoutPreferencesView
from workout_plan.views.progress_views.get_exercise_progress_view import GetExerciseProgressView
from workout_plan.views.progress_views.get_progress_summary_view import GetProgressSummaryView
from workout_plan.views.session_views.delete_workout_session_view import DeleteWorkoutSessionView
from workout_plan.views.session_views.get_workout_session_view import GetWorkoutSessionView
from workout_plan.views.session_views.paginate_workout_sessions_view import PaginateWorkoutSessionsView
from workout_plan.views.session_views.start_workout_session_view import StartWorkoutSessionView
from workout_plan.views.session_views.update_workout_session_view import UpdateWorkoutSessionView
from workout_plan.views.set_log_views.delete_set_log_view import DeleteSetLogView
from workout_plan.views.set_log_views.log_set_view import LogSetView
from workout_plan.views.set_log_views.update_set_log_view import UpdateSetLogView

api, router = ApiRouterCreator.create_api_and_router('workout-plan', WorkoutPlanPermissionChecker())

# --- Exercise library ---
ListExercisesView.register_get(router, 'exercises/')
CreateExerciseView.register_post(router, 'exercises/')
UpdateExerciseView.register_patch_by_id(router, prefix='exercises')
DeleteExerciseView.register_delete_by_id(router, prefix='exercises')

# --- Plans ---
PaginateWorkoutPlansView.register_get(router, 'plans/')
CreateWorkoutPlanView.register_post(router, 'plans/')
GetWorkoutPlanView.register_get(router, 'plans/{int:object_id}/')
UpdateWorkoutPlanView.register_patch_by_id(router, prefix='plans')
DeleteWorkoutPlanView.register_delete_by_id(router, prefix='plans')
ShareWorkoutPlanView.register_post(router, 'plans/{int:object_id}/share/')
UnshareWorkoutPlanView.register_post(router, 'plans/{int:object_id}/unshare/')
ListWorkoutPlanMembersView.register_get(router, 'plans/{int:object_id}/members/')
ReorderPlanDaysView.register_post(router, 'plans/{int:plan_id}/reorder-days/')

# --- Days ---
CreatePlanDayView.register_post(router, 'days/')
UpdatePlanDayView.register_patch_by_id(router, prefix='days')
DeletePlanDayView.register_delete_by_id(router, prefix='days')
ReorderPlanExercisesView.register_post(router, 'days/{int:day_id}/reorder-exercises/')

# --- Exercises in a day ---
CreatePlanExerciseView.register_post(router, 'plan-exercises/')
UpdatePlanExerciseView.register_patch_by_id(router, prefix='plan-exercises')
DeletePlanExerciseView.register_delete_by_id(router, prefix='plan-exercises')

# --- Sessions and logged sets ---
PaginateWorkoutSessionsView.register_get(router, 'sessions/')
StartWorkoutSessionView.register_post(router, 'sessions/')
GetWorkoutSessionView.register_get(router, 'sessions/{int:object_id}/')
UpdateWorkoutSessionView.register_patch_by_id(router, prefix='sessions')
DeleteWorkoutSessionView.register_delete_by_id(router, prefix='sessions')
LogSetView.register_post(router, 'set-logs/')
UpdateSetLogView.register_patch_by_id(router, prefix='set-logs')
DeleteSetLogView.register_delete_by_id(router, prefix='set-logs')

# --- Progress and preferences ---
GetProgressSummaryView.register_get(router, 'progress/')
GetExerciseProgressView.register_get(router, 'progress/exercises/{int:exercise_id}/')
GetWorkoutPreferencesView.register_get(router, 'preferences/')
UpdateWorkoutPreferencesView.register_post(router, 'preferences/')

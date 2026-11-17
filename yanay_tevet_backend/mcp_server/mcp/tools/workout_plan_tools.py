from django.db.models import Q
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from mcp_server.mcp.context import get_current_user
from mcp_server.mcp.schemas.workout_plan_schemas import (
    DeletedWorkoutPlanDayResult,
    RemovedWorkoutPlanExercisesResult,
    WorkoutPlanDayInput,
    WorkoutPlanExerciseChange,
    WorkoutPlanExerciseInput,
    WorkoutSessionList,
)
from mcp_server.mcp.tool_errors import handle_tool_errors
from users.models import User
from workout_plan.enums.muscle_group import MuscleGroup
from workout_plan.enums.tracking_type import TrackingType
from workout_plan.managers.exercise_manager import ExerciseManager
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.managers.workout_progress_manager import WorkoutProgressManager
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.exercise_progress_permission_checker import ExerciseProgressPermissionChecker
from workout_plan.permissions_checkers.usable_exercise_permission_checker import UsableExercisePermissionChecker
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.permissions_checkers.workout_plan_permission_checker import WorkoutPlanPermissionChecker
from workout_plan.serializers.exercise_serializers.exercise_serializer import (
    ExerciseSchema,
    ExerciseSerializer,
    ExerciseWritableSchema,
)
from workout_plan.serializers.plan_serializers.plan_day_serializer import PlanDaySchema, PlanDaySerializer
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import (
    PlanExerciseSchema,
    PlanExerciseSerializer,
    PlanExerciseTargetsSchema,
)
from workout_plan.serializers.plan_serializers.workout_plan_detail_serializer import (
    WorkoutPlanDetailSchema,
    WorkoutPlanDetailSerializer,
)
from workout_plan.serializers.plan_serializers.workout_plan_serializer import (
    WorkoutPlanSchema,
    WorkoutPlanSerializer,
)
from workout_plan.serializers.progress_serializers.progress_schemas import (
    ExerciseHistorySummarySchema,
    ExerciseProgressSchema,
)
from workout_plan.serializers.session_serializers.workout_session_serializer import WorkoutSessionSerializer

READ_ONLY = ToolAnnotations(readOnlyHint=True)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True)


async def _get_user() -> User:
    """The connected user, provided they have the Workout Plan app (the web API checks the same at router
    level)."""
    user = await get_current_user()
    await WorkoutPlanPermissionChecker().async_raise_exception_if_not_valid(user)
    return user


async def _load_plan(user: User, plan_id: int) -> WorkoutPlan:
    plan = await WorkoutPlan.objects.filter(id=plan_id).afirst()
    if plan is None:
        raise ObjectDoesntExistAPIException(WorkoutPlan, plan_id)
    await WorkoutPlanMemberPermissionChecker(plan).async_raise_exception_if_not_valid(user)
    return plan


async def _load_day(user: User, day_id: int) -> PlanDay:
    day = await PlanDay.objects.filter(id=day_id).afirst()
    if day is None:
        raise ObjectDoesntExistAPIException(PlanDay, day_id)
    await WorkoutPlanMemberPermissionChecker(day.plan_id).async_raise_exception_if_not_valid(user)
    return day


async def _load_plan_exercises(user: User, plan_exercise_ids: list[int]) -> list[PlanExercise]:
    unique_ids = list(dict.fromkeys(plan_exercise_ids))
    by_id = {pe.id: pe async for pe in PlanExercise.objects.filter(id__in=unique_ids)}
    for plan_exercise_id in unique_ids:
        if plan_exercise_id not in by_id:
            raise ObjectDoesntExistAPIException(PlanExercise, plan_exercise_id)
    for day_id in {pe.day_id for pe in by_id.values()}:
        await _load_day(user, day_id)
    return [by_id[plan_exercise_id] for plan_exercise_id in unique_ids]


async def _load_exercises(user: User, entries: list[WorkoutPlanExerciseInput]) -> dict[int, Exercise]:
    """Check every exercise up front, so a plan is either built whole or not at all."""
    ids = list(dict.fromkeys(entry.exercise_id for entry in entries))
    by_id = {exercise.id: exercise async for exercise in Exercise.objects.filter(id__in=ids)}
    for exercise_id in ids:
        if exercise_id not in by_id:
            raise ObjectDoesntExistAPIException(Exercise, exercise_id)
        await UsableExercisePermissionChecker(by_id[exercise_id]).async_raise_exception_if_not_valid(user)
    return by_id


def _targets(entry: WorkoutPlanExerciseInput) -> PlanExerciseTargetsSchema:
    return PlanExerciseTargetsSchema(**entry.model_dump(exclude_unset=True, exclude={'exercise_id'}))


async def _add_exercises(
    manager: WorkoutPlanManager, day: PlanDay, entries: list[WorkoutPlanExerciseInput], exercises: dict[int, Exercise],
) -> list[PlanExercise]:
    return [await manager.add_exercise(day, exercises[entry.exercise_id], _targets(entry)) for entry in entries]


def register(mcp: FastMCP) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_workout_exercises(search: str | None = None, muscle_group: MuscleGroup | None = None) -> list[ExerciseSchema]:
        """List the exercise library you can use in a plan: the built-in catalog (English + Hebrew names),
        your own exercises, and ones from plans shared with you. Optional search matches either name.
        Each exercise has a tracking_type (reps, weight_reps, time, distance, laps) and per_side (each arm
        or leg logged separately). Look here before create_workout_exercise, to avoid duplicates."""
        user = await _get_user()
        exercises = ExerciseManager(user).visible_exercises()
        if search:
            exercises = exercises.filter(Q(name_en__icontains=search) | Q(name_he__icontains=search))
        if muscle_group is not None:
            exercises = exercises.filter(muscle_group=muscle_group)
        return await ExerciseSerializer().serialize_query(exercises)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def create_workout_exercise(
        muscle_group: MuscleGroup,
        tracking_type: TrackingType,
        name_en: str = '',
        name_he: str = '',
        per_side: bool = False,
    ) -> ExerciseSchema:
        """Add an exercise to your own library when the catalog has nothing that matches. Give a name in
        English, Hebrew or both. tracking_type: weight_reps for machines and free weights, reps for
        body-weight moves, time for holds (plank), distance for running, laps for pool swimming."""
        user = await _get_user()
        exercise = await ExerciseManager(user).create_custom(ExerciseWritableSchema(
            name_en=name_en, name_he=name_he, muscle_group=muscle_group, tracking_type=tracking_type,
            per_side=per_side,
        ))
        return await ExerciseSerializer().serialize(exercise)

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_workout_plans() -> list[WorkoutPlanSchema]:
        """List the workout plans you own or that are shared with you, most recently changed first."""
        user = await _get_user()
        plans = WorkoutPlan.objects.filter(memberships__user_id=user.id).distinct().order_by('-updated_at')
        return await WorkoutPlanSerializer().serialize_query(plans)

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def get_workout_plan(plan_id: int) -> WorkoutPlanDetailSchema:
        """Get a workout plan: its every-day section (done on every training day, e.g. swimming, running,
        abs) and its days (Day 1, Day 2…), each with its exercises and targets."""
        user = await _get_user()
        return await WorkoutPlanDetailSerializer().serialize(await _load_plan(user, plan_id))

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def create_workout_plan(
        name: str,
        days: list[WorkoutPlanDayInput],
        every_day_exercises: list[WorkoutPlanExerciseInput] | None = None,
        pool_length_m: int = 25,
    ) -> WorkoutPlanDetailSchema:
        """Create a workout plan owned by you, e.g. from a photo of a handwritten program. days are the
        day types in order (name them as the program does, e.g. 'יום 1 – גב ויד קדמית'); every_day_exercises
        are done on every day. Find exercise ids with list_workout_exercises first and create missing
        ones with create_workout_exercise. Put the program's per-exercise remarks (e.g. 'heavy weight',
        'first set light') in notes. pool_length_m turns swimming laps into distance."""
        user = await _get_user()
        every_day_entries = every_day_exercises or []
        exercises = await _load_exercises(
            user, every_day_entries + [entry for day in days for entry in day.exercises],
        )
        manager = WorkoutPlanManager(user)
        plan = await manager.create_plan(name, pool_length_m)
        await _add_exercises(manager, await manager.get_every_day(plan), every_day_entries, exercises)
        for day_input in days:
            day = await manager.add_day(plan, day_input.name)
            await _add_exercises(manager, day, day_input.exercises, exercises)
        return await WorkoutPlanDetailSerializer().serialize(plan)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def update_workout_plan(plan_id: int, name: str | None = None, pool_length_m: int | None = None) -> WorkoutPlanDetailSchema:
        """Rename a workout plan or change its pool length."""
        user = await _get_user()
        plan = await _load_plan(user, plan_id)
        await WorkoutPlanManager(user).update_plan(plan, name, pool_length_m)
        return await WorkoutPlanDetailSerializer().serialize(plan)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def add_workout_plan_day(plan_id: int, name: str, exercises: list[WorkoutPlanExerciseInput] | None = None) -> PlanDaySchema:
        """Add a day type to the end of a plan, optionally with its exercises."""
        user = await _get_user()
        plan = await _load_plan(user, plan_id)
        entries = exercises or []
        by_id = await _load_exercises(user, entries)
        manager = WorkoutPlanManager(user)
        day = await manager.add_day(plan, name)
        await _add_exercises(manager, day, entries, by_id)
        return await PlanDaySerializer().serialize(day)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def rename_workout_plan_day(day_id: int, name: str) -> PlanDaySchema:
        """Rename a day of a plan."""
        user = await _get_user()
        day = await _load_day(user, day_id)
        await WorkoutPlanManager(user).rename_day(day, name)
        return await PlanDaySerializer().serialize(day)

    @mcp.tool(annotations=DESTRUCTIVE)
    @handle_tool_errors
    async def delete_workout_plan_day(day_id: int) -> DeletedWorkoutPlanDayResult:
        """Delete a day of a plan with its exercise entries. Logged workouts are kept. The every-day
        section cannot be deleted."""
        user = await _get_user()
        day = await _load_day(user, day_id)
        # Captured up front: Django clears an instance's id once it is deleted.
        deleted_id = day.id
        exercise_count = await WorkoutPlanManager(user).delete_day(day)
        return DeletedWorkoutPlanDayResult(deleted_day_id=deleted_id, deleted_exercise_count=exercise_count)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def add_workout_plan_exercises(day_id: int, exercises: list[WorkoutPlanExerciseInput]) -> list[PlanExerciseSchema]:
        """Add exercises to the end of a day (or of the every-day section, by its day id)."""
        user = await _get_user()
        day = await _load_day(user, day_id)
        by_id = await _load_exercises(user, exercises)
        added = await _add_exercises(WorkoutPlanManager(user), day, exercises, by_id)
        serializer = PlanExerciseSerializer()
        return [await serializer.serialize(pe) for pe in added]

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def update_workout_plan_exercises(changes: list[WorkoutPlanExerciseChange]) -> list[PlanExerciseSchema]:
        """Change the targets, rest time or notes of exercises in a plan (e.g. raise the weight or reps
        as the trainee progresses)."""
        user = await _get_user()
        entries = {pe.id: pe for pe in await _load_plan_exercises(user, [c.plan_exercise_id for c in changes])}
        manager = WorkoutPlanManager(user)
        for change in changes:
            targets = PlanExerciseTargetsSchema(**change.model_dump(exclude_unset=True, exclude={'plan_exercise_id'}))
            await manager.update_exercise(entries[change.plan_exercise_id], targets)
        serializer = PlanExerciseSerializer()
        return [await serializer.serialize(pe) for pe in entries.values()]

    @mcp.tool(annotations=DESTRUCTIVE)
    @handle_tool_errors
    async def remove_workout_plan_exercises(plan_exercise_ids: list[int]) -> RemovedWorkoutPlanExercisesResult:
        """Remove exercises from their days. Workouts already logged for them are kept."""
        user = await _get_user()
        entries = await _load_plan_exercises(user, plan_exercise_ids)
        removed_ids = [pe.id for pe in entries]
        manager = WorkoutPlanManager(user)
        for entry in entries:
            await manager.remove_exercise(entry)
        return RemovedWorkoutPlanExercisesResult(removed_plan_exercise_ids=removed_ids)

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_workout_sessions(limit: int = 20) -> WorkoutSessionList:
        """Your logged workouts, newest first: date, plan and day, how many sets and exercises."""
        user = await _get_user()
        sessions = WorkoutSession.objects.filter(user_id=user.id).order_by('-started_at', '-id')[:max(1, min(limit, 100))]
        return WorkoutSessionList(sessions=await WorkoutSessionSerializer().serialize_query(sessions))

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_workout_progress() -> list[ExerciseHistorySummarySchema]:
        """The exercises you have logged, with how many workouts each and the last date — the starting
        point for get_workout_progress."""
        user = await _get_user()
        return await WorkoutProgressManager(user).history_summary()

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def get_workout_progress(exercise_id: int) -> ExerciseProgressSchema:
        """Your numbers for one exercise per workout, oldest first: heaviest set and volume for weights
        (and per arm/leg for one-sided exercises), reps, hold time, distance and pace for running, laps,
        distance and pace per 100 m for swimming. Only your own logs, even on a shared plan."""
        user = await _get_user()
        exercise = await Exercise.objects.filter(id=exercise_id).afirst()
        if exercise is None:
            raise ObjectDoesntExistAPIException(Exercise, exercise_id)
        await ExerciseProgressPermissionChecker(exercise).async_raise_exception_if_not_valid(user)
        return await WorkoutProgressManager(user).exercise_progress(exercise)

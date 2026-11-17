from django.db.models import Max
from django.utils import timezone

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.enums.invitation_membership_type import InvitationMembershipType
from users.enums.permissions import Permissions
from users.managers.invitation_manager import InvitationManager, InvitationResult
from users.models import Invitation, User
from users.schemas.invitation_schema import InvitationMembership
from workout_plan.enums.tracking_type import TrackingType
from workout_plan.enums.workout_plan_role import WorkoutPlanRole
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_plan_membership import WorkoutPlanMembership
from workout_plan.permissions_checkers.usable_exercise_permission_checker import UsableExercisePermissionChecker
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import PlanExerciseTargetsSchema


class WorkoutPlanManager:
    def __init__(self, user: User) -> None:
        self.user = user

    # --- Plans ---

    async def create_plan(self, name: str, pool_length_m: int | None = None) -> WorkoutPlan:
        plan = await WorkoutPlan.objects.acreate(
            owner_id=self.user.id, name=name.strip(), pool_length_m=pool_length_m or 25,
        )
        await WorkoutPlanMembership.objects.acreate(plan_id=plan.id, user_id=self.user.id, role=WorkoutPlanRole.OWNER)
        await PlanDay.objects.acreate(plan_id=plan.id, is_every_day=True, name='', order=0)
        return plan

    async def update_plan(self, plan: WorkoutPlan, name: str | None, pool_length_m: int | None) -> None:
        if name is not None and name.strip():
            plan.name = name.strip()
        if pool_length_m is not None and pool_length_m > 0:
            plan.pool_length_m = pool_length_m
        await plan.asave()

    async def get_every_day(self, plan: WorkoutPlan) -> PlanDay:
        day, _ = await PlanDay.objects.aget_or_create(plan_id=plan.id, is_every_day=True, defaults={'name': ''})
        return day

    async def _touch(self, plan_id: int) -> None:
        await WorkoutPlan.objects.filter(id=plan_id).aupdate(updated_at=timezone.now())

    # --- Sharing ---

    async def _find_user(self, identifier: str) -> User | None:
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, plan: WorkoutPlan, identifier: str) -> InvitationResult:
        """An existing user gets access right away, an unknown email a pending invitation. Either way the
        invitee also gets the Workout Plan app, so they can open the plan."""
        identifier = identifier.strip()
        target = await self._find_user(identifier)
        if target is not None:
            if target.id == plan.owner_id:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='The owner already has this plan.',
                    error_code='cannot_share_with_owner',
                )
            email = target.email
        elif '@' in identifier:
            email = identifier
        else:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}". Invite them by email instead.',
                error_code='user_not_found',
            )
        membership = InvitationMembership(
            type=InvitationMembershipType.WORKOUT_PLAN,
            object_id=plan.id,
            role=WorkoutPlanRole.COLLABORATOR.value,
        )
        return await InvitationManager(self.user).invite(
            email=email, permissions=[Permissions.WORKOUT_PLAN], membership=membership,
        )

    async def unshare(self, plan: WorkoutPlan, identifier: str) -> None:
        target = await self._find_user(identifier.strip())
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}".',
                error_code='user_not_found',
            )
        if target.id == plan.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='The owner cannot be removed from the plan.',
                error_code='cannot_remove_owner',
            )
        await WorkoutPlanMembership.objects.filter(plan_id=plan.id, user_id=target.id).adelete()

    async def list_members(self, plan: WorkoutPlan) -> list[WorkoutPlanMembership]:
        return [m async for m in WorkoutPlanMembership.objects.filter(plan_id=plan.id).order_by('id')]

    async def list_pending_invitations(self, plan: WorkoutPlan) -> list[Invitation]:
        return await InvitationManager().list_pending_for_membership(InvitationMembershipType.WORKOUT_PLAN, plan.id)

    # --- Days ---

    async def add_day(self, plan: WorkoutPlan, name: str) -> PlanDay:
        aggregate = await PlanDay.objects.filter(plan_id=plan.id, is_every_day=False).aaggregate(max_order=Max('order'))
        next_order = 0 if aggregate['max_order'] is None else aggregate['max_order'] + 1
        day = await PlanDay.objects.acreate(plan_id=plan.id, name=name.strip(), order=next_order)
        await self._touch(plan.id)
        return day

    async def rename_day(self, day: PlanDay, name: str) -> None:
        day.name = name.strip()
        await day.asave()
        await self._touch(day.plan_id)

    async def ensure_day_deletable(self, day: PlanDay) -> None:
        if day.is_every_day:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='The every-day section cannot be deleted.',
                error_code='cannot_delete_every_day',
            )

    async def delete_day(self, day: PlanDay) -> int:
        """Delete a day with its entries; returns how many entries went with it. Logged sets are kept."""
        await self.ensure_day_deletable(day)
        entry_count = await PlanExercise.objects.filter(day_id=day.id).acount()
        plan_id = day.plan_id
        await day.adelete()
        await self._touch(plan_id)
        return entry_count

    async def reorder_days(self, plan: WorkoutPlan, ordered_ids: list[int]) -> None:
        days = {day.id: day async for day in PlanDay.objects.filter(plan_id=plan.id, is_every_day=False)}
        for index, day_id in enumerate(ordered_ids):
            if day_id in days:
                days[day_id].order = index
        await PlanDay.objects.abulk_update(list(days.values()), ['order'])
        await self._touch(plan.id)

    # --- Exercises in a day ---

    async def add_exercise(self, day: PlanDay, exercise: Exercise, targets: PlanExerciseTargetsSchema) -> PlanExercise:
        await UsableExercisePermissionChecker(exercise).async_raise_exception_if_not_valid(self.user)
        aggregate = await PlanExercise.objects.filter(day_id=day.id).aaggregate(max_order=Max('order'))
        next_order = 0 if aggregate['max_order'] is None else aggregate['max_order'] + 1
        plan_exercise = PlanExercise(day_id=day.id, exercise_id=exercise.id, order=next_order)
        self._apply_targets(plan_exercise, targets, TrackingType(exercise.tracking_type), is_new=True)
        await plan_exercise.asave()
        await self._touch(day.plan_id)
        return plan_exercise

    async def update_exercise(self, plan_exercise: PlanExercise, targets: PlanExerciseTargetsSchema) -> None:
        exercise = await Exercise.objects.aget(id=plan_exercise.exercise_id)
        self._apply_targets(plan_exercise, targets, TrackingType(exercise.tracking_type), is_new=False)
        await plan_exercise.asave()
        day = await plan_exercise.get_day()
        if day is not None:
            await self._touch(day.plan_id)

    async def remove_exercise(self, plan_exercise: PlanExercise) -> None:
        day = await plan_exercise.get_day()
        await plan_exercise.adelete()
        if day is not None:
            await self._touch(day.plan_id)

    async def reorder_exercises(self, day: PlanDay, ordered_ids: list[int]) -> None:
        entries = {pe.id: pe async for pe in PlanExercise.objects.filter(day_id=day.id)}
        for index, entry_id in enumerate(ordered_ids):
            if entry_id in entries:
                entries[entry_id].order = index
        await PlanExercise.objects.abulk_update(list(entries.values()), ['order'])
        await self._touch(day.plan_id)

    @staticmethod
    def _apply_targets(
        plan_exercise: PlanExercise, targets: PlanExerciseTargetsSchema, tracking_type: TrackingType, is_new: bool,
    ) -> None:
        fields = targets.model_dump(exclude_unset=True)
        if targets.target_sets is not None:
            plan_exercise.target_sets = max(1, targets.target_sets)
        if 'rest_seconds' in fields and targets.rest_seconds is not None:
            plan_exercise.rest_seconds = targets.rest_seconds
        if 'notes' in fields:
            plan_exercise.notes = (targets.notes or '').strip()
        if 'target_reps' in fields:
            plan_exercise.target_reps = targets.target_reps
        if 'target_weight_kg' in fields:
            plan_exercise.target_weight_kg = targets.target_weight_kg
        if 'target_seconds' in fields:
            plan_exercise.target_seconds = targets.target_seconds
        if 'target_distance_km' in fields:
            plan_exercise.target_distance_km = targets.target_distance_km
        if 'target_laps' in fields:
            plan_exercise.target_laps = targets.target_laps
        if is_new and targets.target_sets is None:
            # Cardio is one long effort; strength defaults to the common 3 sets.
            is_cardio = tracking_type in (TrackingType.DISTANCE, TrackingType.LAPS)
            plan_exercise.target_sets = 1 if is_cardio else 3

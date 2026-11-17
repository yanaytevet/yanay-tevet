from django.test import TestCase
from mcp.server.auth.middleware.auth_context import auth_context_var
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.mcp.server import build_mcp_server
from users.enums.permissions import Permissions
from users.models import User
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.workout_plan import WorkoutPlan


class WorkoutPlanMcpToolsTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            username='noam@example.com', email='noam@example.com', permissions=[Permissions.WORKOUT_PLAN])
        cls.no_app_user = User.objects.create(username='other@example.com', email='other@example.com')
        cls.lat_pulldown = Exercise.objects.get(catalog_key='lat_pulldown')
        cls.swimming = Exercise.objects.get(catalog_key='swimming')

    def _as(self, user: User) -> None:
        token = AccessToken(token='t', client_id='c', scopes=[], subject=str(user.id))
        auth_context_var.set(AuthenticatedUser(token))

    async def test_create_workout_plan_builds_days_and_every_day_section(self) -> None:
        self._as(self.user)
        mcp = build_mcp_server()
        await mcp.call_tool('create_workout_plan', {
            'name': 'Noam',
            'every_day_exercises': [{'exercise_id': self.swimming.id, 'target_laps': 40}],
            'days': [{'name': 'Day 1', 'exercises': [
                {'exercise_id': self.lat_pulldown.id, 'target_sets': 4, 'target_reps': 12, 'notes': 'heavy'},
            ]}],
        })
        plan = await WorkoutPlan.objects.aget(owner_id=self.user.id)
        entries = [pe async for pe in PlanExercise.objects.filter(day__plan_id=plan.id).order_by('-day__is_every_day')]
        self.assertEqual([pe.exercise_id for pe in entries], [self.swimming.id, self.lat_pulldown.id])
        self.assertEqual(entries[0].target_sets, 1)
        self.assertEqual(entries[1].notes, 'heavy')

    async def test_an_unknown_exercise_creates_nothing(self) -> None:
        self._as(self.user)
        mcp = build_mcp_server()
        with self.assertRaises(ToolError):
            await mcp.call_tool('create_workout_plan', {
                'name': 'Broken', 'days': [{'name': 'Day 1', 'exercises': [{'exercise_id': 999999}]}],
            })
        self.assertFalse(await WorkoutPlan.objects.filter(owner_id=self.user.id).aexists())

    async def test_a_user_without_the_app_is_refused(self) -> None:
        self._as(self.no_app_user)
        mcp = build_mcp_server()
        with self.assertRaises(ToolError):
            await mcp.call_tool('create_workout_plan', {'name': 'Nope', 'days': []})
        self.assertFalse(await WorkoutPlan.objects.filter(owner_id=self.no_app_user.id).aexists())

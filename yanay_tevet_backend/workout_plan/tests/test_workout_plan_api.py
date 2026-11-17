import json

from django.test import TestCase

from common.testing.authenticated_client import AuthenticatedClient
from users.enums.permissions import Permissions
from users.models import User
from workout_plan.models.exercise import Exercise
from workout_plan.models.set_log import SetLog

API = '/api/workout-plan'


class WorkoutPlanApiTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.owner = User.objects.create(
            username='owner@example.com', email='owner@example.com', permissions=[Permissions.WORKOUT_PLAN])
        cls.partner = User.objects.create(
            username='partner@example.com', email='partner@example.com', permissions=[Permissions.WORKOUT_PLAN])
        cls.stranger = User.objects.create(
            username='stranger@example.com', email='stranger@example.com', permissions=[Permissions.WORKOUT_PLAN])
        cls.lat_pulldown = Exercise.objects.get(catalog_key='lat_pulldown')
        cls.swimming = Exercise.objects.get(catalog_key='swimming')

    async def _json(self, response) -> dict:
        self.assertLess(response.status_code, 300, response.content)
        return json.loads(response.content)

    async def _plan_with_day(self, client: AuthenticatedClient) -> tuple[dict, dict, dict]:
        plan = await self._json(await client.post_json(f'{API}/plans/', {'name': 'Noam', 'pool_length_m': 25}))
        day = await self._json(await client.post_json(f'{API}/days/', {'plan_id': plan['id'], 'name': 'Day 1'}))
        entry = await self._json(await client.post_json(f'{API}/plan-exercises/', {
            'day_id': day['id'], 'exercise_id': self.lat_pulldown.id, 'target_sets': 4, 'target_reps': 12,
        }))
        return plan, day, entry

    async def test_a_new_plan_has_an_every_day_section(self) -> None:
        plan, _, _ = await self._plan_with_day(AuthenticatedClient(self.owner))
        self.assertIsNotNone(plan['every_day'])
        self.assertTrue(plan['every_day']['is_every_day'])

    async def test_only_members_see_a_plan_and_sharing_lets_the_partner_in(self) -> None:
        owner = AuthenticatedClient(self.owner)
        plan, _, _ = await self._plan_with_day(owner)
        self.assertEqual((await AuthenticatedClient(self.stranger).get(f'{API}/plans/{plan["id"]}/')).status_code, 403)

        await self._json(await owner.post_json(f'{API}/plans/{plan["id"]}/share/', {'identifier': 'partner@example.com'}))
        detail = await self._json(await AuthenticatedClient(self.partner).get(f'{API}/plans/{plan["id"]}/'))
        self.assertEqual(detail['days'][0]['exercises'][0]['target_reps'], 12)

    async def test_logs_are_personal_on_a_shared_plan(self) -> None:
        owner = AuthenticatedClient(self.owner)
        plan, day, entry = await self._plan_with_day(owner)
        await owner.post_json(f'{API}/plans/{plan["id"]}/share/', {'identifier': 'partner@example.com'})
        session = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))

        partner = AuthenticatedClient(self.partner)
        self.assertEqual((await partner.get(f'{API}/sessions/{session["id"]}/')).status_code, 403)
        response = await partner.post_json(f'{API}/set-logs/', {
            'session_id': session['id'], 'exercise_id': self.lat_pulldown.id, 'set_number': 1, 'reps': 12,
        })
        self.assertEqual(response.status_code, 403)

    async def test_logging_the_same_set_twice_updates_it(self) -> None:
        owner = AuthenticatedClient(self.owner)
        _, day, entry = await self._plan_with_day(owner)
        session = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        payload = {
            'session_id': session['id'], 'exercise_id': self.lat_pulldown.id, 'plan_exercise_id': entry['id'],
            'set_number': 1, 'reps': 12, 'weight_kg': 40,
        }
        await self._json(await owner.post_json(f'{API}/set-logs/', payload))
        await self._json(await owner.post_json(f'{API}/set-logs/', {**payload, 'reps': 10}))
        logs = [log async for log in SetLog.objects.filter(session_id=session['id'])]
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].reps, 10)

    async def test_reopening_a_day_resumes_the_unfinished_session(self) -> None:
        owner = AuthenticatedClient(self.owner)
        _, day, _ = await self._plan_with_day(owner)
        first = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        second = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        self.assertEqual(first['id'], second['id'])

        await self._json(await owner.patch(f'{API}/sessions/{first["id"]}/', {'finished': True}, content_type='application/json'))
        third = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        self.assertNotEqual(first['id'], third['id'])

    async def test_progress_takes_the_heaviest_set_and_previous_logs_prefill(self) -> None:
        owner = AuthenticatedClient(self.owner)
        _, day, entry = await self._plan_with_day(owner)
        first = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        for number, weight in ((1, 40), (2, 45)):
            await self._json(await owner.post_json(f'{API}/set-logs/', {
                'session_id': first['id'], 'exercise_id': self.lat_pulldown.id, 'plan_exercise_id': entry['id'],
                'set_number': number, 'reps': 12, 'weight_kg': weight,
            }))
        await owner.patch(f'{API}/sessions/{first["id"]}/', {'finished': True}, content_type='application/json')

        second = await self._json(await owner.post_json(f'{API}/sessions/', {'day_id': day['id']}))
        self.assertEqual([log['weight_kg'] for log in second['previous_logs']], [40, 45])

        progress = await self._json(await owner.get(f'{API}/progress/exercises/{self.lat_pulldown.id}/'))
        self.assertEqual(progress['points'][0]['top_weight_kg'], 45)
        self.assertEqual(progress['points'][0]['volume_kg'], 40 * 12 + 45 * 12)

    async def test_swimming_laps_turn_into_distance_with_the_pool_length(self) -> None:
        owner = AuthenticatedClient(self.owner)
        plan, _, _ = await self._plan_with_day(owner)
        session = await self._json(await owner.post_json(f'{API}/sessions/', {'plan_id': plan['id']}))
        await self._json(await owner.post_json(f'{API}/set-logs/', {
            'session_id': session['id'], 'exercise_id': self.swimming.id, 'set_number': 1,
            'laps': 40, 'duration_seconds': 1200,
        }))
        progress = await self._json(await owner.get(f'{API}/progress/exercises/{self.swimming.id}/'))
        self.assertEqual(progress['points'][0]['distance_km'], 1.0)
        self.assertEqual(progress['points'][0]['pace_seconds_per_100m'], 120.0)

    async def test_a_custom_exercise_is_private_until_it_is_in_a_shared_plan(self) -> None:
        owner = AuthenticatedClient(self.owner)
        custom = await self._json(await owner.post_json(f'{API}/exercises/', {
            'name_he': 'חבל מעמד', 'muscle_group': 'triceps', 'tracking_type': 'weight_reps',
        }))
        partner = AuthenticatedClient(self.partner)
        names = [e['id'] for e in (await self._json(await partner.get(f'{API}/exercises/')))['exercises']]
        self.assertNotIn(custom['id'], names)

        plan, day, _ = await self._plan_with_day(owner)
        await self._json(await owner.post_json(f'{API}/plan-exercises/', {'day_id': day['id'], 'exercise_id': custom['id']}))
        await owner.post_json(f'{API}/plans/{plan["id"]}/share/', {'identifier': 'partner@example.com'})
        names = [e['id'] for e in (await self._json(await partner.get(f'{API}/exercises/')))['exercises']]
        self.assertIn(custom['id'], names)
        self.assertEqual((await partner.delete(f'{API}/exercises/{custom["id"]}/')).status_code, 403)

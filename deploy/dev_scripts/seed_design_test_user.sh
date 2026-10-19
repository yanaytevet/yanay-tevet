#!/usr/bin/env bash
# Local dev only: a non-admin user with every app permission and sample task projects, for checking UI
# changes in the browser without your own account. Sign in with the username and password below.
# Run from deploy/dev_scripts/. Safe to re-run: it resets the password and only seeds an empty account.
set -e

DEV_TEST_USERNAME="design-test"
DEV_TEST_PASSWORD="dev-5a-9mMNm1P88u6o-"

bash run_manage.sh shell -c "
import datetime
from django.utils import timezone
from users.models import User
from users.enums.permissions import Permissions
from task_management.models.task import Task
from task_management.models.task_project import TaskProject
from task_management.models.task_project_membership import TaskProjectMembership
from task_management.enums.project_role import ProjectRole
from task_management.enums.project_status import ProjectStatus
from task_management.enums.task_priority import TaskPriority
from task_management.enums.task_status import TaskStatus

user, _ = User.objects.get_or_create(username='${DEV_TEST_USERNAME}', defaults={'first_name': 'Design', 'last_name': 'Test'})
user.set_password('${DEV_TEST_PASSWORD}')
user.permissions = [p for p in Permissions.get_list() if p != Permissions.ADMIN and p != Permissions.EDITOR]
user.save()

if not TaskProject.objects.filter(owner=user).exists():
    now = timezone.now()

    def project(name, description='', status=ProjectStatus.ACTIVE):
        p = TaskProject.objects.create(owner=user, name=name, description=description, status=status)
        TaskProjectMembership.objects.create(project=p, user=user, role=ProjectRole.OWNER)
        return p

    def task(p, name, order, **fields):
        return Task.objects.create(project=p, created_by=user, name=name, order=order, **fields)

    trip = project('Trip to Japan', 'Two weeks in April: Tokyo, Kyoto and a few days in the Alps.')
    task(trip, 'Renew passport', 1, priority=TaskPriority.URGENT, due_at=now - datetime.timedelta(days=2))
    task(trip, 'Book flights to Tokyo', 2, priority=TaskPriority.HIGH, due_at=now + datetime.timedelta(days=3))
    gear = task(trip, 'Pack the camera gear', 3, priority=TaskPriority.MEDIUM)
    task(trip, 'Charge batteries', 1, parent=gear, status=TaskStatus.DONE, completed_at=now)
    task(trip, 'Clean lenses', 2, parent=gear)
    task(trip, 'Format SD cards', 3, parent=gear)
    task(trip, 'Water the plants', 4, is_repeating=True, repeat_days=[])
    task(trip, 'Read the rail pass guide', 5, priority=TaskPriority.LOW, description='Check which trains the pass covers')
    task(trip, 'לתאם עם המשפחה את התאריכים', 6)
    task(trip, 'Choose travel dates', 7, status=TaskStatus.DONE, completed_at=now)
    task(trip, 'Set a budget', 8, status=TaskStatus.DONE, completed_at=now)

    home = project('Home renovation', 'Kitchen first, then the balcony.')
    task(home, 'Pick tiles', 1, status=TaskStatus.DONE, completed_at=now)
    task(home, 'Get three quotes', 2, status=TaskStatus.DONE, completed_at=now)

    project('Old move checklist', status=ProjectStatus.ARCHIVED)

print('Seeded', user.username)
"

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
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.models.shopping_list_membership import ShoppingListMembership
from shopping_lists.enums.shopping_list_role import ShoppingListRole
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.models.itinerary_item import ItineraryItem
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.enums.list_status import ListStatus
from itinerary_lists.enums.item_status import ItemStatus
from workout_plan.models.workout_routine import WorkoutRoutine
from workout_plan.models.workout_exercise import WorkoutExercise
from workout_plan.enums.measurement_type import MeasurementType
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.models.special_date import SpecialDate
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership
from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.enums.special_date_category import SpecialDateCategory
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.models.project_membership import ProjectMembership
from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.enums.project_role import ProjectRole as RentalProjectRole
from apartment_hunt.enums.prospect_status import ProspectStatus
from apartment_hunt.enums.currency import Currency

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

if not ShoppingList.objects.filter(owner=user).exists():
    groceries = ShoppingList.objects.create(owner=user, name='Groceries')
    ShoppingListMembership.objects.create(shopping_list=groceries, user=user, role=ShoppingListRole.OWNER)
    for order, (name, checked) in enumerate([('Milk', False), ('Eggs', False), ('Tomatoes', False), ('חומוס', False), ('Bread', True), ('Coffee beans', True)]):
        ShoppingItem.objects.create(shopping_list=groceries, created_by=user, name=name, is_checked=checked, order=order)

if not ItineraryList.objects.filter(owner=user).exists():
    camping = ItineraryList.objects.create(owner=user, name='Camping weekend', description='Everything for two nights in the Galilee.', status=ListStatus.ACTIVE, activated_at=timezone.now())
    ItineraryListMembership.objects.create(itinerary_list=camping, user=user, role=ListRole.OWNER)
    for order, (name, status) in enumerate([('Tent', ItemStatus.IN_THE_CAR), ('Sleeping bags', ItemStatus.READY), ('Gas canister', ItemStatus.NEED_TO_BUY), ('Head torches', ItemStatus.IN_THE_HOUSE)]):
        ItineraryItem.objects.create(itinerary_list=camping, created_by=user, name=name, status=status, order=order)

if not WorkoutRoutine.objects.filter(user=user).exists():
    legs = WorkoutRoutine.objects.create(user=user, name='Leg day', order=1)
    WorkoutExercise.objects.create(routine=legs, name='Squats', measurement_type=MeasurementType.REPS, notes='Keep the knees out', order=1)
    WorkoutExercise.objects.create(routine=legs, name='Plank', measurement_type=MeasurementType.TIME, order=2)
    WorkoutRoutine.objects.create(user=user, name='Upper body', order=2)

if not SpecialDate.objects.filter(created_by=user).exists():
    # The app creates a default calendar on first visit, so reuse one if it is there.
    family = SpecialDateCalendar.objects.filter(owner=user).first()
    if family is None:
        family = SpecialDateCalendar.objects.create(owner=user, name='משפחה')
        SpecialDateCalendarMembership.objects.create(calendar=family, user=user, role=SpecialDateCalendarRole.OWNER)
    today = timezone.localdate()
    SpecialDate.objects.create(created_by=user, calendar=family, name='יום ההולדת של סבתא', category=SpecialDateCategory.BIRTHDAY, date=today.replace(year=1948) + datetime.timedelta(days=5))
    SpecialDate.objects.create(created_by=user, calendar=family, name='יום הנישואין של ההורים', category=SpecialDateCategory.ANNIVERSARY, date=today.replace(year=1985) + datetime.timedelta(days=40))
    SpecialDate.objects.create(created_by=user, calendar=family, name='Dana', category=SpecialDateCategory.BIRTHDAY, date=today.replace(year=1992) - datetime.timedelta(days=20))

if not RentalProject.objects.filter(owner=user, app=ProjectApp.APARTMENT_HUNT).exists():
    hunt = RentalProject.objects.create(owner=user, app=ProjectApp.APARTMENT_HUNT, name='Tel Aviv, spring', description='Two bedrooms, near a park.', currency=Currency.NIS)
    ProjectMembership.objects.create(project=hunt, user=user, role=RentalProjectRole.OWNER)
    ApartmentProspect.objects.create(project=hunt, created_by=user, title='Bright 3-room on Dizengoff', status=ProspectStatus.SAW, town='Tel Aviv', monthly_rent=7800, rooms=3, floor=2, size_sqm=75, liked_level=4)
    ApartmentProspect.objects.create(project=hunt, created_by=user, title='Florentin loft', status=ProspectStatus.CONTACTED, town='Tel Aviv', monthly_rent=6900, rooms=2.5, floor=4, size_sqm=60, liked_level=3)
    ApartmentProspect.objects.create(project=hunt, created_by=user, title='Garden flat, Ramat Gan', status=ProspectStatus.NEED_TO_DECIDE, town='Ramat Gan', monthly_rent=7200, rooms=3, floor=0, size_sqm=80, has_protected_room=True, liked_level=5)

print('Seeded', user.username)
"

from dataclasses import dataclass

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.models.special_date import SpecialDate
from special_dates.models.special_date_calendar import SpecialDateCalendar, generate_join_token
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership
from special_dates.permissions_checkers.special_date_calendar_member_permission_checker import (
    SpecialDateCalendarMemberPermissionChecker,
)
from users.enums.invitation_membership_type import InvitationMembershipType
from users.managers.invitation_manager import InvitationManager, InvitationResult
from users.models import Invitation, User
from users.schemas.invitation_schema import InvitationMembership

PERSONAL_CALENDAR_NAME = 'התאריכים שלי'
MAX_OWNED_CALENDARS = 10


@dataclass
class CalendarWithMembership:
    calendar: SpecialDateCalendar
    membership: SpecialDateCalendarMembership


class SpecialDateCalendarManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_personal_calendar(self) -> None:
        """Every user always owns at least one calendar (so they can keep private dates even after joining shared ones),
        and events from before calendars existed get attached to it."""
        calendar = await SpecialDateCalendar.objects.filter(owner_id=self.user.id).order_by('created_at', 'id').afirst()
        if calendar is None:
            calendar = await self._create(PERSONAL_CALENDAR_NAME)
        await SpecialDate.objects.filter(created_by_id=self.user.id, calendar__isnull=True).aupdate(calendar=calendar)

    async def _create(self, name: str) -> SpecialDateCalendar:
        calendar = await SpecialDateCalendar.objects.acreate(owner_id=self.user.id, name=name)
        await SpecialDateCalendarMembership.objects.acreate(
            calendar_id=calendar.id, user_id=self.user.id, role=SpecialDateCalendarRole.OWNER,
        )
        return calendar

    async def create(self, name: str) -> SpecialDateCalendar:
        if await SpecialDateCalendar.objects.filter(owner_id=self.user.id).acount() >= MAX_OWNED_CALENDARS:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message=f'אפשר ליצור עד {MAX_OWNED_CALENDARS} לוחות.',
                error_code='special_date_calendars_limit_reached',
            )
        return await self._create(name.strip())

    async def list_for_user(self) -> list[CalendarWithMembership]:
        return [
            CalendarWithMembership(calendar=membership.calendar, membership=membership)
            async for membership in SpecialDateCalendarMembership.objects.filter(user_id=self.user.id)
            .select_related('calendar').order_by('calendar__created_at', 'calendar__id')
        ]

    async def calendar_ids(self, include_hidden: bool = True) -> list[int]:
        memberships = SpecialDateCalendarMembership.objects.filter(user_id=self.user.id)
        if not include_hidden:
            memberships = memberships.filter(hide_from_upcoming=False)
        return [calendar_id async for calendar_id in memberships.values_list('calendar_id', flat=True)]

    async def get_member_calendar(self, calendar_id: int) -> SpecialDateCalendar:
        """Loads a calendar the user is a member of, or raises 404/403."""
        calendar = await SpecialDateCalendar.objects.filter(id=calendar_id).afirst()
        if calendar is None:
            raise ObjectDoesntExistAPIException(SpecialDateCalendar, calendar_id)
        await SpecialDateCalendarMemberPermissionChecker(calendar).async_raise_exception_if_not_valid(self.user)
        return calendar

    async def get_membership(self, calendar: SpecialDateCalendar) -> SpecialDateCalendarMembership | None:
        return await SpecialDateCalendarMembership.objects.filter(calendar_id=calendar.id, user_id=self.user.id).afirst()

    async def raise_if_last_owned(self, calendar: SpecialDateCalendar) -> None:
        if await SpecialDateCalendar.objects.filter(owner_id=self.user.id).exclude(id=calendar.id).aexists():
            return
        raise RestAPIException(
            status_code=StatusCode.HTTP_400_BAD_REQUEST,
            message='זה הלוח האחרון שלך ולכן אי אפשר למחוק אותו. אפשר לשנות לו את השם.',
            error_code='cannot_delete_last_calendar',
        )

    async def rename(self, calendar: SpecialDateCalendar, name: str) -> None:
        calendar.name = name.strip()
        await calendar.asave(update_fields=['name', 'updated_at'])

    async def reset_join_token(self, calendar: SpecialDateCalendar) -> None:
        calendar.join_token = generate_join_token()
        await calendar.asave(update_fields=['join_token', 'updated_at'])

    async def set_hide_from_upcoming(self, calendar: SpecialDateCalendar, hide: bool) -> None:
        await SpecialDateCalendarMembership.objects.filter(
            calendar_id=calendar.id, user_id=self.user.id
        ).aupdate(hide_from_upcoming=hide)

    @staticmethod
    async def get_by_join_token(token: str) -> SpecialDateCalendar:
        calendar = await SpecialDateCalendar.objects.filter(join_token=token).afirst()
        if calendar is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message='קישור ההצטרפות לא תקף. בקשו קישור חדש מבעלי הלוח.',
                error_code='invalid_join_token',
            )
        return calendar

    async def join_by_token(self, token: str) -> SpecialDateCalendar:
        calendar = await self.get_by_join_token(token)
        await SpecialDateCalendarMembership.objects.aget_or_create(
            calendar_id=calendar.id, user_id=self.user.id, defaults={'role': SpecialDateCalendarRole.EDITOR},
        )
        return calendar

    async def leave(self, calendar: SpecialDateCalendar) -> None:
        if calendar.owner_id == self.user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='הבעלים לא יכול/ה לעזוב את הלוח. אפשר למחוק אותו.',
                error_code='owner_cannot_leave',
            )
        await SpecialDateCalendarMembership.objects.filter(calendar_id=calendar.id, user_id=self.user.id).adelete()

    async def _find_user(self, identifier: str) -> User | None:
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, calendar: SpecialDateCalendar, identifier: str) -> InvitationResult:
        """Existing users join right away; an unknown email gets a pending invitation + email and joins on sign-up."""
        identifier = identifier.strip()
        target = await self._find_user(identifier)
        if target is not None:
            if target.id == calendar.owner_id:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='הבעלים כבר נמצא/ת בלוח.',
                    error_code='cannot_share_with_owner',
                )
            email = target.email
        elif '@' in identifier:
            email = identifier
        else:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'לא נמצא משתמש בשם "{identifier}". אפשר להזמין לפי כתובת מייל.',
                error_code='user_not_found',
            )
        membership = InvitationMembership(
            type=InvitationMembershipType.SPECIAL_DATE_CALENDAR,
            object_id=calendar.id,
            role=SpecialDateCalendarRole.EDITOR.value,
        )
        return await InvitationManager(self.user).invite(email=email, permissions=[], membership=membership)

    async def remove_member(self, calendar: SpecialDateCalendar, user_id: int) -> None:
        if user_id == calendar.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='אי אפשר להסיר את הבעלים מהלוח.',
                error_code='cannot_remove_owner',
            )
        await SpecialDateCalendarMembership.objects.filter(calendar_id=calendar.id, user_id=user_id).adelete()

    async def list_members(self, calendar: SpecialDateCalendar) -> list[SpecialDateCalendarMembership]:
        return [m async for m in SpecialDateCalendarMembership.objects.filter(calendar_id=calendar.id).order_by('created_at', 'id')]

    async def list_pending_invitations(self, calendar: SpecialDateCalendar) -> list[Invitation]:
        return await InvitationManager().list_pending_for_membership(
            InvitationMembershipType.SPECIAL_DATE_CALENDAR, calendar.id
        )

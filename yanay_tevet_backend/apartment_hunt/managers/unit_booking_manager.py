from datetime import date
from typing import Optional

from apartment_hunt.enums.project_role import ProjectRole
from apartment_hunt.models.project_membership import ProjectMembership
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.models.unit_booking import UnitBooking
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class UnitBookingManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def can_manage_all(self, project: RentalProject) -> bool:
        """Site admins and project owners can see every booker's name and manage any booking."""
        if self.user.is_admin():
            return True
        membership = await ProjectMembership.objects.filter(
            project_id=project.id, user_id=self.user.id, role=ProjectRole.OWNER
        ).afirst()
        return membership is not None

    async def _raise_if_overlapping(self, unit_id: int, start_date: date, end_date: date, exclude_id: int | None) -> None:
        # Two ranges overlap when each starts before the other ends.
        query = UnitBooking.objects.filter(unit_id=unit_id, start_date__lt=end_date, end_date__gt=start_date)
        if exclude_id is not None:
            query = query.exclude(id=exclude_id)
        if await query.afirst() is not None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_409_CONFLICT,
                message='Those dates are already booked.',
                error_code='dates_unavailable',
            )

    async def create_booking(self, unit_id: int, start_date: date, end_date: date, note: str) -> UnitBooking:
        if end_date <= start_date:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Check-out must be after check-in.',
                error_code='invalid_date_range',
            )
        await self._raise_if_overlapping(unit_id, start_date, end_date, exclude_id=None)
        booking = UnitBooking(
            unit_id=unit_id,
            created_by_id=self.user.id,
            start_date=start_date,
            end_date=end_date,
            note=note,
        )
        await booking.asave()
        return booking

    async def update_booking(
        self,
        booking: UnitBooking,
        note: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> UnitBooking:
        if start_date is not None:
            booking.start_date = start_date
        if end_date is not None:
            booking.end_date = end_date
        if note is not None:
            booking.note = note
        if booking.end_date <= booking.start_date:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Check-out must be after check-in.',
                error_code='invalid_date_range',
            )
        await self._raise_if_overlapping(booking.unit_id, booking.start_date, booking.end_date, exclude_id=booking.id)
        await booking.asave()
        return booking

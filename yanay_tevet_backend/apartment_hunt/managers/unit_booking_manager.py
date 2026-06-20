from datetime import date

from apartment_hunt.models.unit_booking import UnitBooking
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class UnitBookingManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_booking(
        self,
        unit_id: int,
        start_date: date,
        end_date: date,
        note: str,
    ) -> UnitBooking:
        if end_date <= start_date:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Check-out must be after check-in.',
                error_code='invalid_date_range',
            )
        # Two ranges overlap when each starts before the other ends.
        overlap = await UnitBooking.objects.filter(
            unit_id=unit_id, start_date__lt=end_date, end_date__gt=start_date
        ).afirst()
        if overlap is not None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_409_CONFLICT,
                message='Those dates are already booked.',
                error_code='dates_unavailable',
            )
        booking = UnitBooking(
            unit_id=unit_id,
            created_by_id=self.user.id,
            start_date=start_date,
            end_date=end_date,
            note=note,
        )
        await booking.asave()
        return booking

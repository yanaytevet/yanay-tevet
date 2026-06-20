from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.models.unit_booking import UnitBooking
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User


class BookingPermissionChecker(PermissionsChecker):
    """A booking can be managed by the member who created it, or by a project owner."""

    def __init__(self, booking: UnitBooking, project: RentalProject) -> None:
        self.booking = booking
        self.project = project

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if user is not None and self.booking.created_by_id == user.id:
            return
        await ProjectMemberPermissionChecker(
            self.project, require_owner=True
        ).async_raise_exception_if_not_valid(user)

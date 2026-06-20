from apartment_hunt.permissions_checkers.villa_villekulla_permission_checker import VillaVillekullaPermissionChecker
from apartment_hunt.views.project_views.create_villa_villekulla_project_view import CreateVillaVillekullaProjectView
from apartment_hunt.views.project_views.delete_rental_project_view import DeleteRentalProjectView
from apartment_hunt.views.project_views.get_rental_project_view import GetRentalProjectView
from apartment_hunt.views.project_views.list_project_members_view import ListProjectMembersView
from apartment_hunt.views.project_views.paginate_villa_villekulla_projects_view import PaginateVillaVillekullaProjectsView
from apartment_hunt.views.project_views.share_villa_villekulla_project_view import ShareVillaVillekullaProjectView
from apartment_hunt.views.project_views.unshare_rental_project_view import UnshareRentalProjectView
from apartment_hunt.views.project_views.update_rental_project_view import UpdateRentalProjectView
from apartment_hunt.views.unit_booking_views.create_unit_booking_view import CreateUnitBookingView
from apartment_hunt.views.unit_booking_views.delete_unit_booking_view import DeleteUnitBookingView
from apartment_hunt.views.unit_booking_views.get_unit_calendar_view import GetUnitCalendarView
from apartment_hunt.views.unit_booking_views.update_unit_booking_view import UpdateUnitBookingView
from apartment_hunt.views.unit_views.create_unit_view import CreateUnitView
from apartment_hunt.views.unit_views.list_units_view import ListUnitsView
from common.django_utils.api_router_creator import ApiRouterCreator

# Villa Villekulla sub-app of Home Sweet Home. Shares the apartment_hunt app but
# has its own permission; projects reuse the RentalProject machinery (app=villa_villekulla).
api, router = ApiRouterCreator.create_api_and_router('villa-villekulla', VillaVillekullaPermissionChecker())

# --- Projects ---
PaginateVillaVillekullaProjectsView.register_get(router, 'projects/')
CreateVillaVillekullaProjectView.register_post(router, 'projects/')
GetRentalProjectView.register_get(router, 'projects/{int:object_id}/')
UpdateRentalProjectView.register_patch_by_id(router, prefix='projects')
DeleteRentalProjectView.register_delete_by_id(router, prefix='projects')
ShareVillaVillekullaProjectView.register_post(router, 'projects/{int:object_id}/share/')
UnshareRentalProjectView.register_post(router, 'projects/{int:object_id}/unshare/')
ListProjectMembersView.register_get(router, 'projects/{int:object_id}/members/')

# --- Units ---
ListUnitsView.register_get(router, 'projects/{int:object_id}/units/')
CreateUnitView.register_post(router, 'units/')

# --- Bookings ---
GetUnitCalendarView.register_get(router, 'units/{int:unit_id}/bookings/')
CreateUnitBookingView.register_post(router, 'bookings/')
UpdateUnitBookingView.register_patch_by_id(router, prefix='bookings')
DeleteUnitBookingView.register_delete_by_id(router, prefix='bookings')

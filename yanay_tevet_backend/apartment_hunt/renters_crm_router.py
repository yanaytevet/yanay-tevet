from apartment_hunt.permissions_checkers.renters_crm_permission_checker import RentersCrmPermissionChecker
from apartment_hunt.views.project_views.create_renters_project_view import CreateRentersProjectView
from apartment_hunt.views.project_views.delete_rental_project_view import DeleteRentalProjectView
from apartment_hunt.views.project_views.get_rental_project_view import GetRentalProjectView
from apartment_hunt.views.project_views.list_project_members_view import ListProjectMembersView
from apartment_hunt.views.project_views.paginate_renters_projects_view import PaginateRentersProjectsView
from apartment_hunt.views.project_views.set_rental_project_status_view import (
    FinishRentalProjectView,
    ReopenRentalProjectView,
)
from apartment_hunt.views.project_views.share_rental_project_view import ShareRentalProjectView
from apartment_hunt.views.project_views.unshare_rental_project_view import UnshareRentalProjectView
from apartment_hunt.views.project_views.update_rental_project_view import UpdateRentalProjectView
from apartment_hunt.views.renter_prospect_views.create_renter_prospect_view import CreateRenterProspectView
from apartment_hunt.views.renter_prospect_views.delete_renter_prospect_view import DeleteRenterProspectView
from apartment_hunt.views.renter_prospect_views.get_renter_prospect_view import GetRenterProspectView
from apartment_hunt.views.renter_prospect_views.paginate_renter_prospects_view import PaginateRenterProspectsView
from apartment_hunt.views.renter_prospect_views.update_renter_prospect_view import UpdateRenterProspectView
from common.django_utils.api_router_creator import ApiRouterCreator

# Renters CRM sub-app of Home Sweet Home. Shares the apartment_hunt app but has
# its own permission; projects reuse the RentalProject machinery (app=renters_crm).
api, router = ApiRouterCreator.create_api_and_router('renters-crm', RentersCrmPermissionChecker())

# --- Projects ---
PaginateRentersProjectsView.register_get(router, 'projects/')
CreateRentersProjectView.register_post(router, 'projects/')
GetRentalProjectView.register_get(router, 'projects/{int:object_id}/')
UpdateRentalProjectView.register_patch_by_id(router, prefix='projects')
DeleteRentalProjectView.register_delete_by_id(router, prefix='projects')
ShareRentalProjectView.register_post(router, 'projects/{int:object_id}/share/')
UnshareRentalProjectView.register_post(router, 'projects/{int:object_id}/unshare/')
ListProjectMembersView.register_get(router, 'projects/{int:object_id}/members/')
FinishRentalProjectView.register_post(router, 'projects/{int:object_id}/finish/')
ReopenRentalProjectView.register_post(router, 'projects/{int:object_id}/reopen/')

# --- Renters ---
PaginateRenterProspectsView.register_get(router, 'projects/{int:project_id}/renters/')
CreateRenterProspectView.register_post(router, 'renters/')
GetRenterProspectView.register_get(router, 'renters/{int:object_id}/')
UpdateRenterProspectView.register_patch_by_id(router, prefix='renters')
DeleteRenterProspectView.register_delete_by_id(router, prefix='renters')

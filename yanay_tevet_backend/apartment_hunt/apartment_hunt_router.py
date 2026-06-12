from apartment_hunt.permissions_checkers.apartment_hunt_permission_checker import ApartmentHuntPermissionChecker
from apartment_hunt.views.project_views.create_rental_project_view import CreateRentalProjectView
from apartment_hunt.views.project_views.delete_rental_project_view import DeleteRentalProjectView
from apartment_hunt.views.project_views.get_rental_project_view import GetRentalProjectView
from apartment_hunt.views.project_views.list_project_members_view import ListProjectMembersView
from apartment_hunt.views.project_views.paginate_rental_projects_view import PaginateRentalProjectsView
from apartment_hunt.views.project_views.share_rental_project_view import ShareRentalProjectView
from apartment_hunt.views.project_views.unshare_rental_project_view import UnshareRentalProjectView
from apartment_hunt.views.project_views.update_rental_project_view import UpdateRentalProjectView
from apartment_hunt.views.prospect_views.create_apartment_prospect_view import CreateApartmentProspectView
from apartment_hunt.views.prospect_views.delete_apartment_image_view import DeleteApartmentImageView
from apartment_hunt.views.prospect_views.delete_apartment_prospect_view import DeleteApartmentProspectView
from apartment_hunt.views.prospect_views.get_apartment_prospect_view import GetApartmentProspectView
from apartment_hunt.views.prospect_views.paginate_apartment_prospects_view import PaginateApartmentProspectsView
from apartment_hunt.views.prospect_views.update_apartment_prospect_view import UpdateApartmentProspectView
from apartment_hunt.views.prospect_views.upload_apartment_prospect_image_view import UploadApartmentProspectImageView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('apartment-hunt', ApartmentHuntPermissionChecker())

# --- Projects ---
PaginateRentalProjectsView.register_get(router, 'projects/')
CreateRentalProjectView.register_post(router, 'projects/')
GetRentalProjectView.register_get(router, 'projects/{int:object_id}/')
UpdateRentalProjectView.register_patch_by_id(router, prefix='projects')
DeleteRentalProjectView.register_delete_by_id(router, prefix='projects')
ShareRentalProjectView.register_post(router, 'projects/{int:object_id}/share/')
UnshareRentalProjectView.register_post(router, 'projects/{int:object_id}/unshare/')
ListProjectMembersView.register_get(router, 'projects/{int:object_id}/members/')

# --- Prospects ---
PaginateApartmentProspectsView.register_get(router, 'projects/{int:project_id}/prospects/')
CreateApartmentProspectView.register_post(router, 'prospects/')
GetApartmentProspectView.register_get(router, 'prospects/{int:object_id}/')
UpdateApartmentProspectView.register_patch_by_id(router, prefix='prospects')
DeleteApartmentProspectView.register_delete_by_id(router, prefix='prospects')
UploadApartmentProspectImageView.register_post(router, 'prospects/{int:object_id}/upload-image/')

# --- Images ---
DeleteApartmentImageView.register_delete_by_id(router, prefix='images')

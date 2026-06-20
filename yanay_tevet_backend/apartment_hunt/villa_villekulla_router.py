from apartment_hunt.permissions_checkers.villa_villekulla_permission_checker import VillaVillekullaPermissionChecker
from common.django_utils.api_router_creator import ApiRouterCreator

# Villa Villekulla sub-app of Home Sweet Home. Shares the apartment_hunt app but
# has its own permission; views are registered here as the sub-app is built out.
api, router = ApiRouterCreator.create_api_and_router('villa-villekulla', VillaVillekullaPermissionChecker())

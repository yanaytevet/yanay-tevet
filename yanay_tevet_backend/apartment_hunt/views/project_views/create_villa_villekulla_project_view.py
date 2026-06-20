from ninja import Path, Schema

from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.managers.rental_project_manager import RentalProjectManager
from apartment_hunt.managers.unit_manager import UnitManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.views.project_views.create_rental_project_view import CreateRentalProjectView
from common.simple_api.api_request import APIRequest


class CreateVillaVillekullaProjectView(CreateRentalProjectView):
    @classmethod
    def get_project_app(cls) -> ProjectApp:
        return ProjectApp.VILLA_VILLEKULLA

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: RentalProject, data: Schema, path: Path) -> None:
        user = await request.future_user
        await RentalProjectManager(user).ensure_owner_membership(obj)
        await UnitManager(user).ensure_default_unit(obj)

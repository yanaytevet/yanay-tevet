from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.views.project_views.paginate_rental_projects_view import PaginateRentalProjectsView


class PaginateVillaVillekullaProjectsView(PaginateRentalProjectsView):
    @classmethod
    def get_project_app(cls) -> ProjectApp:
        return ProjectApp.VILLA_VILLEKULLA

from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.views.project_views.create_rental_project_view import CreateRentalProjectView


class CreateRentersProjectView(CreateRentalProjectView):
    @classmethod
    def get_project_app(cls) -> ProjectApp:
        return ProjectApp.RENTERS_CRM

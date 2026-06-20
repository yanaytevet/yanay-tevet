from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.models.unit import Unit
from users.models import User


class UnitManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_default_unit(self, project: RentalProject) -> Unit:
        unit = await Unit.objects.filter(project_id=project.id).order_by('id').afirst()
        if unit is None:
            unit = Unit(project_id=project.id, name='The Unit')
            await unit.asave()
        return unit

    async def list_units(self, project: RentalProject) -> list[Unit]:
        return [u async for u in Unit.objects.filter(project_id=project.id).order_by('id')]

    async def create_unit(self, project_id: int, name: str, description: str) -> Unit:
        unit = Unit(project_id=project_id, name=name, description=description)
        await unit.asave()
        return unit

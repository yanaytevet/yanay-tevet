from decimal import Decimal
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.enums.currency import Currency
from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.managers.rental_project_manager import RentalProjectManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.serializers.rental_project_serializers.rental_project_serializer import RentalProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.schema_config import hidden_fields_config
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateRentalProjectSchema(Schema):
    model_config = hidden_fields_config('owner_id', 'app')
    owner_id: Optional[int] = None
    app: ProjectApp = ProjectApp.APARTMENT_HUNT
    name: str
    description: str = ''
    currency: Currency = Currency.NIS
    initial_asked_rent: Optional[Decimal] = None


class CreateRentalProjectView(CreateItemAPIView):
    @classmethod
    def get_project_app(cls) -> ProjectApp:
        return ProjectApp.APARTMENT_HUNT

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateRentalProjectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return RentalProjectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return RentalProject

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateRentalProjectSchema, path: Path) -> CreateRentalProjectSchema:
        data.owner_id = (await request.future_user).id
        data.app = cls.get_project_app()
        return data

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: RentalProject, data: Schema, path: Path) -> None:
        user = await request.future_user
        await RentalProjectManager(user).ensure_owner_membership(obj)

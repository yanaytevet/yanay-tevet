from typing import Type

from django.db.models import Model

from .rest_api_exception import RestAPIException
from ..enums.status_code import StatusCode


class ObjectDoesntExistAPIException(RestAPIException):
    def __init__(self, model_class: Type[Model], object_id: int | None):
        self.model_class = model_class
        self.object_id = object_id
        self.msg = f'{model_class.__name__} with id {object_id} was not found'
        super().__init__(StatusCode.HTTP_404_NOT_FOUND, 'object_was_not_found', self.msg)

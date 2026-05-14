from typing import Type

from django.db.models import Model

from .rest_api_exception import RestAPIException
from ..enums.status_code import StatusCode


class ObjectIdIsMissingAPIException(RestAPIException):
    def __init__(self, model_class: Type[Model]):
        self.model_class = model_class
        self.msg = f'{model_class.__name__} object with a none object id could not be searched'
        super().__init__(StatusCode.HTTP_404_NOT_FOUND, 'object_id_missing', self.msg)

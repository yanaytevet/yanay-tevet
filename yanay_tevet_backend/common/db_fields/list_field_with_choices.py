from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField
from django.forms import CheckboxSelectMultiple, MultipleChoiceField


class ListFieldWithChoices(ArrayField):
    def __init__(self, *args, **kwargs):
        self.default = kwargs.pop("default", list)
        self.choices = kwargs.pop("choices", [])
        self.max_length = kwargs.pop("max_length", 100)
        self.blank = kwargs.get("blank", True)
        self.null = kwargs.pop("null", True)

        base_field = CharField(  # type: ignore
            max_length=self.max_length,
            choices=self.choices,  # type: ignore
            blank=self.blank,
            null=self.null,  # type: ignore
        )
        kwargs["base_field"] = base_field
        kwargs["default"] = self.default

        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)  # type: ignore

    def formfield(self, **kwargs):
        defaults = {
            "form_class": MultipleChoiceField,
            "choices": self.base_field.choices,
            "widget": CheckboxSelectMultiple,
            "initial": self.default,
            **kwargs,
        }
        return super(ArrayField, self).formfield(**defaults)

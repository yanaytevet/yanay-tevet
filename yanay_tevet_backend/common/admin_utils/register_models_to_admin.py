import inspect
from typing import Type, List, Any

from asgiref.sync import async_to_sync
from django.contrib import admin
from django.db.models import ManyToOneRel, ManyToManyField, ManyToManyRel, Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from common.admin_utils.admin_action import AdminAction
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath


class ModelRegisterer:
    '''
    models can have the following class fields:
    list_display
    list_filter
    search_fields
    raw_id_fields
    '''

    def __init__(self, models,
                 ignore_models: List[Type[Model]] = None,
                 actions_by_model: dict[Type[Model], list[AdminAction]] = None,
                 ):
        self.models = models
        self.ignore_models = ignore_models
        self.actions_by_model = actions_by_model or {}

    def register(self) -> None:
        ignore_models_set = set() if self.ignore_models is None else set(self.ignore_models)
        for name, klass in inspect.getmembers(self.models, inspect.isclass):
            if klass in ignore_models_set:
                continue
            self.register_class(name, klass)

    def register_class(self, name: str, klass: Type[Model]) -> None:
        ignore_fields = getattr(klass, 'ignore_fields') if hasattr(klass, 'ignore_fields') else []
        if hasattr(klass, 'list_display'):
            list_display = getattr(klass, 'list_display')
        else:
            list_display = []
            for field in klass._meta.get_fields():
                if isinstance(field, ManyToOneRel):
                    continue
                if isinstance(field, ManyToManyRel):
                    continue
                if isinstance(field, ManyToManyField):
                    continue
                list_display.append(field.name)
        list_filter = getattr(klass, 'list_filter') if hasattr(klass, 'list_filter') else []

        if hasattr(klass, 'raw_id_fields'):
            raw_id_fields = getattr(klass, 'raw_id_fields')
        else:
            raw_id_fields = []

        search_fields = getattr(klass, 'search_fields') if hasattr(klass, 'search_fields') else []
        action_buttons = self.actions_by_model.get(klass) or []

        def render_change_form(
                self,
                request: HttpRequest,
                context: dict[str, Any],
                add: bool = False,
                change: bool = False,
                form_url: str = "",
                obj: Model | None = None,
        ):
            context["action_buttons"] = [{"name": ab.label, "label": ab.label} for ab in action_buttons]
            return admin.ModelAdmin.render_change_form(self, request, context, add, change, form_url, obj)

        def response_change(self, request: HttpRequest, obj: Model) -> HttpResponse:
            for action_button in action_buttons:
                if action_button.label in request.POST:
                    if action_button.callback:
                        async_to_sync(action_button.callback)(obj.id)
                        return HttpResponseRedirect(".")
                    else:
                        view_obj = action_button.download_file_by_id_view_class()
                        return async_to_sync(view_obj.create_file_response)(
                            None,
                            None,
                            ItemByIdPath(object_id=obj.id)
                        )
            return admin.ModelAdmin.response_change(self, request, obj)

        admin_cls = type('{}_admin'.format(name), (admin.ModelAdmin,), {
            'list_display': list_display,
            'search_fields': search_fields,
            'list_filter': list_filter,
            'raw_id_fields': raw_id_fields,
            'exclude': ignore_fields,
            'change_form_template': 'change_form.html',
            'render_change_form': render_change_form,
            'response_change': response_change,
        })
        admin.site.register(klass, admin_cls)

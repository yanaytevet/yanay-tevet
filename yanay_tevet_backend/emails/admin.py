import json
import types as builtin_types
from typing import Type, Union, get_args, get_origin

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path
from pydantic import BaseModel

from emails.email_classes_loader import EmailClassesLoader
from emails.models import EmailTemplate


def _get_input_type(annotation) -> str:
    if annotation is bool:
        return 'checkbox'
    if annotation in (int, float):
        return 'number'
    if annotation is str:
        return 'text'
    origin = get_origin(annotation)
    if origin is Union or isinstance(annotation, builtin_types.UnionType):
        inner = [a for a in get_args(annotation) if a is not type(None)]
        if inner:
            return _get_input_type(inner[0])
    return 'json'


def _get_form_fields(context_class: Type[BaseModel]) -> list[dict]:
    fields = []
    for name, field_info in context_class.model_fields.items():
        input_type = _get_input_type(field_info.annotation)
        if field_info.is_required():
            default = ''
        else:
            raw = field_info.default
            if raw is None:
                default = ''
            elif input_type == 'json':
                default = json.dumps(raw)
            else:
                default = raw
        fields.append({
            'name': name,
            'input_type': input_type,
            'default': default,
            'required': field_info.is_required(),
        })
    return fields


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    def get_urls(self):
        custom_urls = [
            path(
                'preview/<str:class_name>/',
                self.admin_site.admin_view(self.preview_view),
                name='emails_emailtemplate_preview',
            ),
            path(
                'render/<str:class_name>/',
                self.admin_site.admin_view(self.render_view),
                name='emails_emailtemplate_render',
            ),
        ]
        return custom_urls + super().get_urls()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        email_classes = EmailClassesLoader.get_email_classes()
        rows = []
        for cls in email_classes.values():
            instance = cls()
            rows.append({
                'name': cls.__name__,
                'template_name': instance.get_template_name(),
                'subject': instance.get_subject(),
            })
        context = {
            **self.admin_site.each_context(request),
            'title': 'Email Templates',
            'email_classes': rows,
            'opts': self.model._meta,
        }
        return render(request, 'admin/emails/emailtemplate/change_list.html', context)

    def preview_view(self, request: HttpRequest, class_name: str) -> HttpResponse:
        email_class = EmailClassesLoader.get_email_class(class_name)
        if email_class is None:
            return HttpResponse(f'Email class {class_name!r} not found.', status=404)
        instance = email_class()
        form_fields = _get_form_fields(email_class.get_context_class())
        context = {
            **self.admin_site.each_context(request),
            'title': f'Preview — {class_name}',
            'class_name': class_name,
            'template_name': instance.get_template_name(),
            'subject': instance.get_subject(),
            'form_fields': form_fields,
            'opts': self.model._meta,
        }
        return render(request, 'admin/emails/emailtemplate/preview.html', context)

    def render_view(self, request: HttpRequest, class_name: str) -> HttpResponse:
        if request.method != 'POST':
            return HttpResponse('Method not allowed.', status=405)
        email_class = EmailClassesLoader.get_email_class(class_name)
        if email_class is None:
            return HttpResponse(f'Email class {class_name!r} not found.', status=404)
        form_fields = _get_form_fields(email_class.get_context_class())
        context_data = {}
        for field in form_fields:
            name = field['name']
            raw = request.POST.get(name, '')
            if field['input_type'] == 'checkbox':
                context_data[name] = name in request.POST
            elif field['input_type'] == 'number':
                try:
                    context_data[name] = int(raw) if raw else 0
                except ValueError:
                    context_data[name] = 0
            elif field['input_type'] == 'json':
                try:
                    context_data[name] = json.loads(raw) if raw.strip() else None
                except json.JSONDecodeError as exc:
                    return HttpResponse(
                        f'Invalid JSON for field "{name}": {exc}', status=400
                    )
            else:
                context_data[name] = raw
        context_obj = email_class.get_context_class()(**context_data)
        html = email_class().generate_html(context_obj)
        return HttpResponse(html)

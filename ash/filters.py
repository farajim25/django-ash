from collections import OrderedDict

from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.filters import FieldListFilter, RelatedFieldListFilter
from django.forms.widgets import Media
from django.utils.translation import gettext_lazy as _


class InputFilter(FieldListFilter):
    template = 'filters/input_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = field.name
        super().__init__(field, request, params, model, model_admin, field_path)

    def lookups(self, request, model_admin):
        return ((),)

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'query_parts': (
                (k, v)
                for k, v in changelist.get_filters_params().items()
                if k != self.parameter_name
            )
        }

    def expected_parameters(self):
        return [self.parameter_name]


class AutoCompleteFilter(RelatedFieldListFilter):
    _request_key = 'DJANGO_ASH_ATOCOMPLETE_ADMIN_MEDIA'
    template = 'filters/auto_complete_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.model_admin = model_admin
        self.form = self.get_form(request)

    def lookups(self, request, model_admin):
        return ((),)

    def value(self):
        return self.used_parameters.get(self.lookup_kwarg)

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg]),
            'query_parts': (
                (k, v)
                for k, v in changelist.get_filters_params().items()
                if k != self.lookup_kwarg
            )
        }

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def has_output(self):
        return True

    def field_choices(self, field, request, model_admin):
        return []

    def get_form(self, request):
        form_class = self._get_form_class(request)
        return form_class(self.used_parameters or None)

    def _get_form_class(self, request):
        fields = self._get_form_fields(request)

        form_class = type(
            str('AutoCompleteForm'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )

        has_media = getattr(request, self._request_key, False)
        if not has_media:
            media = Media(
                js=['admin/js/autocomplete-filter.js']
            )
            form_class.base_media = form_class.media
            form_class.filter_media = media
            setattr(request, self._request_key, True)

        return form_class

    def _get_field_widget(self, request):
        return widgets.AutocompleteSelect(
            field=self.field,
            admin_site=self.model_admin.admin_site,
            attrs={'style': "width: 100%", 'autocomplete-filter': True}
        )

    def _get_form_fields(self, request):
        return OrderedDict(
            (
                (self.lookup_kwarg, forms.ModelChoiceField(
                    self.field.remote_field.model.objects.all(),
                    label='',
                    widget=self._get_field_widget(request),
                    required=False,
                    initial=self.value(),
                )),
            )
        )

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(**self.used_parameters)
        return queryset

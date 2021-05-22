from collections import OrderedDict

from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.filters import FieldListFilter
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


class AutoCompleteFilter(FieldListFilter):
    template = 'filters/auto_complete_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = field.name
        super().__init__(field, request, params, model, model_admin, field_path)
        self.model_admin = model_admin
        self.form = self.get_form(request)

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

    def get_form(self, request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters or None)

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str('AutoCompleteForm'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )
        return form_class

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.parameter_name, forms.ModelChoiceField(
                    self.field.remote_field.model.objects.all(),
                    label='',
                    widget=widgets.AutocompleteSelect(
                        field=self.field,
                        admin_site=self.model_admin.admin_site,
                        attrs={'style': "width: 100%",
                               'onchange': "submit_ac_form(this)"}
                    ),
                    required=False,
                    initial=self.value(),
                )),
            )
        )

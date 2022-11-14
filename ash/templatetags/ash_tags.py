from ash import settings
from django import template
from django.apps import apps
from django.contrib.admin import widgets as AdminWidgets
from django.contrib.admin.views.main import PAGE_VAR
from django.contrib.messages import constants
from django.forms import BaseForm
from django.forms import widgets as FormWidgets
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def ash_get_setting(setting_name):
    return getattr(settings, setting_name)


@register.simple_tag
def ash_get_model_icon(app_label):
    conf = apps.get_app_config(app_label)
    return getattr(conf, 'ASH_APP_ICON', settings.ASH_APPS_DEFAULT_ICON)


@register.simple_tag
def ash_form_class_setter(form, **kwargs):
    if isinstance(form, BaseForm):
        for field in form:
            ash_form_field_class_setter(field, **kwargs)

    return str()


@register.simple_tag
def ash_form_field_class_setter(field, **kwargs):
    ash_form_field_widget_class_setter(field.field.widget, **kwargs)
    return field


@register.simple_tag
def ash_form_field_widget_class_setter(widget, **kwargs):
    default_new_class = 'form-control px-2'

    small_widget = kwargs.get('small_widget', False)

    if isinstance(widget, AdminWidgets.AdminSplitDateTime):
        if small_widget:
            widget.template_name = 'admin/widgets/split_datetime_small.html'

        for w in widget.widgets:
            ash_form_field_widget_class_setter(w)

        return widget

    if isinstance(widget, AdminWidgets.RelatedFieldWidgetWrapper):
        ash_form_field_widget_class_setter(widget.widget)
        return widget

    if isinstance(widget, AdminWidgets.AdminRadioSelect):
        return widget

    if isinstance(widget, AdminWidgets.AdminFileWidget):
        old_class = widget.attrs.get('class', '')
        widget.attrs['class'] = f'{old_class} vFileField {default_new_class}'
        return widget

    if isinstance(widget, FormWidgets.ChoiceWidget):
        old_class = widget.attrs.get('class', '')
        widget.attrs['class'] = f'{old_class} vNumberField {default_new_class}'
        return widget

    if isinstance(widget, FormWidgets.CheckboxInput):
        old_class = widget.attrs.get('class', '')
        widget.attrs['class'] = f'{old_class} px-2'
        return widget

    if isinstance(widget, FormWidgets.PasswordInput):
        old_class = widget.attrs.get('class', '')
        widget.attrs['class'] = f'{old_class} vLargeTextField {default_new_class}'
        return widget

    if isinstance(widget, FormWidgets.NumberInput):
        old_class = widget.attrs.get('class', '')
        widget.attrs['class'] = f'{old_class} vNumberField {default_new_class}'
        return widget

    # general case
    old_class = widget.attrs.get('class', '')
    widget.attrs['class'] = f'{old_class} {default_new_class}'
    return widget


@register.simple_tag
def ash_messages_class_setter(messages):
    def add_extra_tag(extra_tags, new_tag):
        if extra_tags:
            return f'{extra_tags} {new_tag} '
        else:
            return new_tag

    for msg in messages:
        level = msg.level
        if level == constants.DEBUG:
            msg.extra_tags = add_extra_tag(msg.extra_tags, 'text-muted')
        elif level == constants.INFO:
            msg.extra_tags = add_extra_tag(msg.extra_tags, 'text-info')
        elif level == constants.SUCCESS:
            msg.extra_tags = add_extra_tag(msg.extra_tags, 'text-success')
        elif level == constants.WARNING:
            msg.extra_tags = add_extra_tag(msg.extra_tags, 'text-warning')
        elif level == constants.ERROR:
            msg.extra_tags = add_extra_tag(msg.extra_tags, 'text-danger')

    return str()


@register.simple_tag
def ash_paginator_number(cl, i):
    link_text = ''
    link_href = ''

    if i == cl.paginator.ELLIPSIS:
        link_text = cl.paginator.ELLIPSIS
        link_href = ''

    elif i == cl.page_num:
        link_href = ''
        link_text = i

    else:
        link_href = f'href={cl.get_query_string({PAGE_VAR: i})}'
        link_text = i

    return format_html(
        '<a {} class="page-link">{}</a>',
        link_href,
        link_text,
    )

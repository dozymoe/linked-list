from django import template
from django.utils.safestring import mark_safe
import logging

_logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def checkbox(bound_field):
    classes = bound_field.field.widget.attrs.get('class', '').split()
    classes.append('mdc-checkbox__native-control')
    attrs = {
        'class': ' '.join(classes),
    }
    return mark_safe(bound_field.as_widget(attrs=attrs))


@register.simple_tag
def text(bound_field):
    classes = bound_field.field.widget.attrs.get('class', '').split()
    classes.append('mdc-text-field__input')
    attrs = {
        'class': ' '.join(classes),
        'aria-labelledby': bound_field.id_for_label + '-label',
    }
    if bound_field.help_text:
        attrs['aria-controls'] = bound_field.id_for_label + '-help'
        attrs['aria-describedby'] = bound_field.id_for_label + '-help'

    return mark_safe(bound_field.as_widget(attrs=attrs))

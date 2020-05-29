from django import template
from django.utils.safestring import mark_safe
import json
import os
import re

register = template.Library()


@register.simple_tag
def stylesheets(module='main'):
    try:
        with open(os.path.join(os.environ['ROOT_DIR'], 'var',
                'webpack-css-meta.json')) as f:
            webpack = json.load(f)
    except OSError:
        return ''
    html = []
    for key, value in webpack.items():
        if not key.endswith('.css'):
            continue
        if re.search(r'(^|~)%s(~|\.)' % module, key):
            html.append('<link href="%s" rel="stylesheet"/>' % value)
    return mark_safe('\n'.join(html))


@register.simple_tag
def javascripts(module='main'):
    try:
        with open(os.path.join(os.environ['ROOT_DIR'], 'var',
                'webpack-js-meta.json')) as f:
            webpack = json.load(f)
    except OSError:
        return ''
    html = []
    for key, value in webpack.items():
        if key == 'runtime.js':
            html.append('<script src="%s"></script>' % value)
        elif re.search(r'(^|~)(base|react|polyfill|%s)(~|\.)' % module, key):
            html.append('<script src="%s"></script>' % value)

    return mark_safe('\n'.join(html))


class CaptureAsNode(template.Node):
    """
    https://chase-seibert.github.io/blog/2010/10/01/check-if-a-block-is-defined-in-django.html
    """
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''


@register.tag
def captureas(parser, token):
    """
    https://chase-seibert.github.io/blog/2010/10/01/check-if-a-block-is-defined-in-django.html
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
                "'capture_as' node requires a variable name.");
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureAsNode(nodelist, args)

from django import template
register = template.Library()

@register.filter
def times(num):
    return 1

@register.filter
def is_none(valor):
    return True
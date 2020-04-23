from django import template
register = template.Library()

@register.filter
def times(num):
    list = []
    num = round(num, 1)
    for x in range(int(num)):
        list.append("")
    return list

@register.filter
def is_none(valor):
    if valor is None:
        return ""
    else:
        return valor
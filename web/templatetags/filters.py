from django import template
from ..models import *
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

@register.filter
def is_save(receta, usuario):
    if Receta_Guardada.objects.filter(receta=receta).filter(usuario=usuario).exists():
        return True
    else:
        return False
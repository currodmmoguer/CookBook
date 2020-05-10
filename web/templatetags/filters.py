from django import template
from ..models import *
register = template.Library()

# Devuelve una lista, con la cantidad redondeada de un número decimal
@register.filter
def times(num):
    list = []
    num = round(num, 1)
    for x in range(int(num)):
        list.append("")
    return list

# Devuelve una cadena vacía en caso de que el valor sea Nono
@register.filter
def is_none(valor):
    if valor is None:
        return ""
    else:
        return valor

# Devuelve un booleano comprobando si un usuario tiene una receta guardada
@register.filter
def is_save(receta, usuario):
    if Receta_Guardada.objects.filter(receta=receta).filter(usuario=usuario).exists():
        return True
    else:
        return False
from django import template
from ..models import *
from datetime import datetime, timezone
from math import trunc

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
def is_none(val):
    if val is None:
        return ""
    else:
        return val

# Devuelve false si no es "" o None
@register.filter
def is_nothing(val):
    if val is "" or val is None:
        return False
    else:
        return True

# Devuelve un booleano comprobando si un usuario tiene una receta guardada
@register.filter
def is_save(receta, usuario):
    if Receta_Guardada.objects.filter(receta=receta).filter(usuario=usuario).exists():
        return True
    else:
        return False

@register.filter
def fecha_hasta_hoy(fecha):
    ahora = datetime.now(timezone.utc)
    diferencia = ahora - fecha
    
    if diferencia.days >= 30:
        tiempo = trunc(diferencia.days / 30)
        medida = "mes" if tiempo == 1 else "meses"
    elif diferencia.days >= 7:
        tiempo = trunc(diferencia.days / 7)
        medida = "semana" if tiempo == 1 else "semanas"
    elif diferencia.days >= 1:
        tiempo = diferencia.days
        medida = "día" if tiempo == 1 else "días"
    elif diferencia.seconds >= 3600:
        tiempo = trunc(diferencia.seconds / 3600)
        medida = "hora" if tiempo == 1 else "horas"
    elif diferencia.seconds >= 60:
        tiempo = trunc(diferencia.seconds / 60)
        medida = "minuto" if tiempo == 1 else "minutos"
    else:
        tiempo = trunc(diferencia.seconds)
        medida = "segundo" if tiempo == 1 else "segundos"

    return str(tiempo) + " " + medida
@register.filter
def capitalize(value):
    return value.capitalize()
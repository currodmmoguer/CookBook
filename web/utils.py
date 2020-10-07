from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from .models import Valoracion, Notificacion, Avg
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.sessions.models import Session



# Paginación
def paginator(request, lista, num=16):
    paginator = Paginator(lista, num)
    num_pagina = request.GET.get('page')
    obj_pagina = paginator.get_page(num_pagina)
    return obj_pagina

# Comprueba que el usuario tiene perfil
def has_profile(request):
    try:
        request.user.perfil
    except ObjectDoesNotExist:
        #Falta mostrar mensaje
        sessions = Session.objects.all()
        logout(request)
        return redirect('login')

def valoracion_media(receta):
    media = Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
    
    if media is None:
        return 0
    else:
        return media


    
def add_notificacion(usuario_origen, usuario_destino, tipo, receta=0, comentario=None):
    if not usuario_origen == usuario_destino:
        notificacion = Notificacion.objects.create(usuario_origen=usuario_origen, usuario_destino=usuario_destino, tipo=tipo)
        
        # En caso que sea comentario o valoracion se debe almacenar a la receta que hace referencia
        if not tipo == "siguiendo":
            notificacion.receta = receta
            if not tipo == "valoracion":    # Solo si es comentario o respuesta
                notificacion.comentario = comentario
            notificacion.save()
            


        
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from .models import Receta, Perfil, Valoracion, Notificacion

from django.db.models import Avg
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from os import remove
# Recortar image
from PIL import Image


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
        return True
    except ObjectDoesNotExist:
        return False


def ordenar_por_valoracion(recetas):
    lista_recetas = []
    for receta in recetas:
        receta.valoracion_media = valoracion_media(receta)
        lista_recetas.append(receta)
            
    lista_recetas.sort(key=lambda x: x.valoracion_media, reverse=True)
    return lista_recetas

# Guarda una receta
def guardar_receta(request, formReceta, formsetPasoFactory, formsetIngredienteFactory):
    receta = None
    formset_paso = formsetPasoFactory(request.POST, request.FILES, prefix='paso')
    formset_ingrediente = formsetIngredienteFactory(request.POST, prefix='ingrediente')

    # Comprueba las validaciones
    if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
        # Receta (básicos)
        receta = formReceta.save(request.POST.__contains__('publico'), request.user)

        # Ingredientes
        for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
            formIngrediente.save(receta)
                
        # Pasos
        pos = 1 # Posición de los pasos
    
        for formPaso in formset_paso:   #Bucle todos los pasos
            formPaso.save(receta, pos)
            pos += 1
    else:   # ERROR
            # En caso de que no sea válido el formulario, muestra los errores
            # Nunca va a dar la situación porque o es requerido, que no 
            # se envía el formulario en caso de que no se introduzca los datos
            # o tiene máximo de caracteres, que no se permite introducir más
            # en el campo de texto
        pass
    
    return receta


def valoracion_media(receta):
    media = Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
    
    if media is None:
        return 0
    else:
        return media


    
def add_notificacion(usuario_origen, usuario_destino, tipo, receta=None, comentario=None):
    if not usuario_origen == usuario_destino:
        notificacion = Notificacion.objects.create(usuario_origen=usuario_origen, usuario_destino=usuario_destino, tipo=tipo)
        
        # En caso que sea comentario o valoracion se debe almacenar a la receta que hace referencia
        if not tipo == "siguiendo":
            notificacion.receta = receta
            if not tipo == "valoracion":    # Solo si es comentario o respuesta
                notificacion.comentario = comentario
            notificacion.save()

def ver_notificaciones(usuario):
    notificaciones = usuario.notificaciones.filter(visto=False)

    for notificacion in notificaciones:
        notificacion.visto = True
        notificacion.save()

def recortar_img(img, valores):
    valores = list(map(float, valores.split(";")))
    image = Image.open(img)
    cropped_image = image.crop((valores[0], valores[1], valores[0] + valores[2], valores[1] + valores[3]))
    resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
    return resized_image
    
def ordenar_recetas(request):
    if "new" == request.POST.get("type-sort"):
        recetas = Receta.objects.filter(publico=True).order_by('-fecha')    #Todas las recetas
        opc = "new"
        
    elif "follow" == request.POST.get("type-sort"):
        siguiendo = Perfil.objects.filter(seguidores=request.user.perfil)
        recetas = Receta.objects.filter(publico=True).filter(usuario__perfil__in=siguiendo).order_by('-fecha')
        opc = "follow"
        
    elif "rating" == request.POST.get("type-sort"):
        recetas = Receta.objects.filter(publico=True)
        recetas = ordenar_por_valoracion(recetas)
        opc = "rating"
    
    return recetas, opc

        
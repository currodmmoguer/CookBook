from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from .models import Valoracion, Avg
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.sessions.models import Session

# Paginación
def paginator(request, lista, num=10):
    paginator = Paginator(lista, num)
    num_pagina = request.GET.get('page')
    obj_pagina = paginator.get_page(num_pagina)
    return obj_pagina

# Comprueba que el usuario tiene perfil
def has_profile(request):
    try:
        request.user.perfil
    except ObjectDoesNotExist:
        print("No existe")
        #Falta mostrar mensaje
        print(request.user.pk)
        sessions = Session.objects.all()
        for session in sessions:
            print(session)
        
        print(request.session.__dict__)
        logout(request)
        return redirect('login')

def valoracion_media(receta):
    return Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
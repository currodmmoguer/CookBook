from django.shortcuts import render, get_object_or_404
#from django.utils import timezone
from .models import *
from .forms import *
from . import utils
from os import remove

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login, logout
#from django.contrib.auth import authenticate
#from django.contrib.auth.forms import UserCreationForm

#Cambiar pass
from django.contrib.auth import update_session_auth_hash
#from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

#Fromset
from django.forms import modelformset_factory, formset_factory

#Contains
from django.db.models import Q

from django.http import HttpResponse, Http404
#from django.urls import reverse

from django.core.exceptions import ObjectDoesNotExist



# Pantalla principal
@login_required
def index(request):

    if not utils.has_profile(request):
        logout(request) # Cierra sesión
        return redirect('login')    # Redirecciona a la pantalla de acceso

    if request.method == "POST":      
        recetas, opc = utils.ordenar_recetas(request)
    else:
        recetas = Receta.objects.filter(publico=True).order_by('-fecha')    #Todas las recetas
        opc = ""
    
    context = {
        'recetas': utils.paginator(request, recetas),
        'opc': opc,
        #'notificaciones': notificaciones,
        'mensaje_vacio': "No hay recetas"
    }
    
    return render(request, 'index.html', context)


"""
    Vistas de recetas
"""

# Vista de una receta creada
@login_required
def receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)  # Obtiene la receta
    
    comentarioFrom = ComentarioForm()
    valoracionForm = ValoracionForm()
    respuestaForm = RespuestaForm()

    # Formulario respuesta a un comentario
    if request.method == 'POST':
        
        if 'comentario-respuesta' in request.POST:
            respuestaForm = RespuestaForm(request.POST)

            if respuestaForm.is_valid():
                padre = Comentario.objects.get(pk=int(request.POST['comentario-respuesta']))
                comentario = respuestaForm.save(receta, request.user)
                utils.add_notificacion(request.user, padre.usuario, "respuesta", receta, comentario)
            
        # Formulario escribir comentario
        if request.method == "POST" and 'comentario' in request.POST:  # En caso de que escriba un comentario
            comentarioForm = ComentarioForm(request.POST)

            if comentarioForm.is_valid():
                comentario = comentarioForm.save(request.user, Receta.objects.get(pk=pk))  # Guarda el texto
                utils.add_notificacion(request.user, receta.usuario, "comentario", receta, comentario)
    
    # Añade a la receta la valoración media
    receta.valoracion_media = utils.valoracion_media(receta)
    
    context = {'receta': receta, 'valoracionForm': valoracionForm,
               'comentarioForm': comentarioFrom, 'respuestaForm': respuestaForm}
    
    return render(request, 'receta.html', context)


# Pantalla formulario crear nueva receta
@login_required
def nueva_receta(request):

    formSugerencia = SugForm()
    formsetPasoFactory = modelformset_factory(Paso, form=PasoFormset, extra=1)
    formsetIngredienteFactory = modelformset_factory(Ingrediente_Receta, form=IngredienteFormset, extra=1)

    if request.method == 'POST':
        formReceta = RecetaForm(request.POST, request.FILES)
        formset_paso = formsetPasoFactory(request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(request.POST, prefix='ingrediente')

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            # Receta (básicos)
            receta = formReceta.save(request.POST.__contains__('publico'), request.user)

            # Ingredientes
            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                formIngrediente.save(receta)
                
            # Pasos
            pos = 1 # Posición de los pasos
    
            for formPaso in formset_paso:   #Bucle todos los 
                formPaso.save(receta, pos)
                pos += 1

            return redirect('receta', pk=receta.pk)

        else:   # ERROR
            # En caso de que no sea válido el formulario, muestra los errores
            # Nunca va a dar la situación porque o es requerido, que no 
            # se envía el formulario en caso de que no se introduzca los datos
            # o tiene máximo de caracteres, que no se permite introducir más
            # en el campo de texto
            pass

    else:   # Si no es POST, crea los formularios vacíos
        formReceta = RecetaForm()
        formset_paso = formsetPasoFactory(queryset=Paso.objects.none(), prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(queryset=Ingrediente.objects.none(), prefix='ingrediente')

    context = {
        'formReceta': formReceta,
        'formsetIngrediente': formset_ingrediente,
        'formsetPaso': formset_paso,
        'categorias': Categoria.objects.all(),
        'formSugerencia': formSugerencia,
    }

    return render(request, 'nueva-receta.html', context)


#Pantalla para editar una receta
@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    formSugerencia = SugForm()
    formsetPasoFactory = modelformset_factory(Paso, form=PasoFormset, extra=0)
    formsetIngredienteFactory = modelformset_factory(Ingrediente_Receta, form=IngredienteFormset, extra=0)

    if request.method == 'POST':
        formReceta = RecetaForm(request.POST, request.FILES, instance=receta)
        formset_paso = formsetPasoFactory(request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(request.POST, prefix='ingrediente')

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            # Receta (básicos)
            receta = formReceta.save(request.POST.__contains__('publico'), request.user)

            # Ingredientes
            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                formIngrediente.save(receta)

            # Pasos
            pos = 1
            
            for formPaso in formset_paso:   #Bucle todos los pasos
                formPaso.save(receta, pos)
                pos += 1

            return redirect('receta', pk=receta.pk)
        
        else:   # ERROR
            # En caso de que no sea válido el formulario, muestra los errores
            # Nunca va a dar la situación porque o es requerido, que no 
            # se envía el formulario en caso de que no se introduzca los datos
            # o tiene máximo de caracteres, que no se permite introducir más
            # en el campo de texto
            pass

    else:   # Si no es POST obtiene rellena los formularios con los datos de la receta
        formReceta = RecetaForm(instance=receta)
        formset_paso = formsetPasoFactory(queryset=Paso.objects.filter(receta=receta).order_by('posicion'), prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(queryset=Ingrediente_Receta.objects.filter(receta=receta), prefix='ingrediente')
        
        # Hace que en el campo ingrediente se muestre el nombre de dicho ingrediente
        # en vez de su id
        for ingrediente in formset_ingrediente:
            id_ingrediente = ingrediente.instance.ingrediente_id
            nombre_ingrediente = Ingrediente.objects.get(id=id_ingrediente).nombre
            ingrediente.__dict__['initial']['ingrediente'] = nombre_ingrediente

    context = {
        'formReceta': formReceta,
        'formsetPaso': formset_paso,
        'formsetIngrediente': formset_ingrediente,
        'categorias': Categoria.objects.all(),
        'formSugerencia': formSugerencia,
    }

    return render(request, 'nueva-receta.html', context)


"""
    Vistas del perfil
"""

#Perfil de un usuario
@login_required
def perfil(request, username):
    user = get_object_or_404(User, username=username)
    
    # Obtiene la lista de los usuarios a los que sigue
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    
    if request.user == user:    # Si el usuario que se visualiza es el mismo del de la sesión
        recetas = user.recetas.all().order_by('-fecha')
        mensaje_vacio = "Aún no tienes ninguna receta creada"
    else:
        recetas = user.recetas.filter(publico=True).order_by('-fecha')
        mensaje_vacio = username + " no tiene ninguna receta creada"

    context = {
        'usuario': user,
        'recetas': utils.paginator(request, recetas),
        'mensaje_vacio': mensaje_vacio,
        'lista_es_receta': True,
    }

    return render(request, 'perfil.html', context)


#Vista del perfil con las recetas guardadas
@login_required
def recetas_guardadas(request, username):
    user = get_object_or_404(User, username=username)
    
    #Comprueba que el perfil es el mismo que el usuario logueado (por motivos de seguridad)
    if not user == request.user:
        return redirect('perfil', username=username)
    
    # Obtiene la lista de los usuarios a los que sigue
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    # Obtiene una lista de las id de recetas que el usuario tiene guardada y ordenada por fecha
    lista_recetas = Receta_Guardada.objects.filter(usuario=user).values_list('receta', flat=True).order_by('-fecha') 
    # Crea una lista de Recetas obtienendolas por su id
    recetas = [Receta.objects.get(pk=id_receta) for id_receta in lista_recetas]
    
    context = {
        'usuario': user,
        'recetas': utils.paginator(request, recetas),
        'mensaje_vacio': "Aún no tienes ninguna receta guardada",
        'lista_es_receta': True,
    }

    return render(request, 'perfil.html', context)


#Vista de perfil con la lista de seguidores
@login_required
def seguidores(request, username):
    user = get_object_or_404(User, username=username)
    # Obtiene la lista de los usuarios a los que sigue
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    # Al obtener la lista de seguidores se obtiene una lista con objetos Perfil, por eso con un bucle se obtiene el objeto usuario de dicho perfil
    seguidores = [i.usuario for i in user.perfil.seguidores.all()]
    
    if user == request.user:
        mensaje_vacio = "Aún no tienes seguidores"
    else:
        mensaje_vacio = username + " no tiene seguidores"
    
    context = {
        'usuario': user,
        'lista_usuarios': utils.paginator(request, seguidores),
        'mensaje_vacio': mensaje_vacio,
        'lista_es_receta': False,
    }

    return render(request, 'perfil.html', context)


#Vista de perfil con la lista de usuarios que sigue
@login_required
def siguiendo(request, username):
    user = get_object_or_404(User, username=username)
    # Obtiene la lista de los usuarios a los que sigue
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    # Al obtener la lista de siguiendo se obtiene una lista con objetos Perfil, por eso con un bucle se obtiene el objeto usuario de dicho perfil
    siguiendo = [i.usuario for i in Perfil.objects.filter(seguidores=user.perfil)]

    if user == request.user:
        mensaje_vacio = "Aún no sigues a nadie"
    else:
        mensaje_vacio = username + " no sigue a nadie"

    context = {
        'usuario': user,
        'lista_usuarios': utils.paginator(request, siguiendo),
        'mensaje_vacio': mensaje_vacio,
        'lista_es_receta': False,
    }

    return render(request, 'perfil.html', context)


#Formulario para editar datos del perfil
@login_required
def editar_perfil(request, username):

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save(request.user)          
        else:   # ERROR
            # No puede haber errores
            print(form.errors)
    else:
        form = EditarPerfilForm(initial={
                'nombre': request.user.first_name,
                'apellido': request.user.last_name,
                'descripcion': request.user.perfil.descripcion,
                'email': request.user.email,
            })

    context = {
        'form': form,
        'opc': 'perfil'
    }

    return render(request, 'editar_perfil.html', context)


# Pantalla para cambiar la contraseña de la cuenta
@login_required
def editar_pass(request, username):
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Se ha actualizado la contraseña correctamente')
            return redirect('editar_pass', username=username)
    
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'opc': 'pass',
    }

    return render(request, 'editar_pass.html', context)

@login_required
def editar_rrss(request):
    user = request.user
    
    if request.method == 'POST':
        form = EditarRRSSForm(request.POST)

        if form.is_valid():
            form.save(request.user.perfil)

    else:
        form = EditarRRSSForm(initial = {
            'facebook': request.user.perfil.facebook,
            'instagram': request.user.perfil.instagram,
            'twitter': request.user.perfil.twitter,
            'youtube': request.user.perfil.youtube
        })

    context = {
        'form': form,
        'opc': 'rrss'
    }

    return render(request, 'editar_rrss.html', context)


"""
    Vistas del navbar
"""

#Notificaciones
@login_required
def notificaciones(request):
    print(request.user.notificaciones)
    notificaciones = Notificacion.objects.filter(usuario_destino=request.user).order_by('-fecha')[:50]
    print(notificaciones)
    utils.ver_notificaciones(request.user)  # Hace que las notificaciones que tengan el atributo "visto" a False lo cambia a True

    context = {
        'notificaciones': notificaciones
    }
    
    return render(request, 'notificaciones.html', context)


#Busqueda avanzada de recetas 
@login_required
def busqueda_avanzada(request):
    form = formset_factory(form=BusquedaAvanzadaForm, extra=1)
    
    if request.method == 'POST':
        formset = form(request.POST)
        ingredientes = []

        if formset.is_valid():
            
            #Por cada input del formulario, obtiene el objeto ingrediente
            for form in formset:   
                ingrediente = Ingrediente.objects.filter(nombre__iexact=form.cleaned_data['ingrediente']).first() #Obtiene el objeto ingrediente a través del nombre

# con is None ya no hace falta: try: except Ingrediente.DoesNotExist:    #Excepción en caso de que no exista un ingrediente con el nombre introducido\n pass    # No hace nada, lo deja pasar
                #Comprueba que no esté en la lista para que no haya repetidos y que exista
                if not ingrediente in ingredientes and not ingrediente is None: 
                    ingredientes.append(ingrediente)
            
            #Obtiene la lista de recetas filtrando por ingrediente y sin obtener repetidos
            #Sqlite no soporta hacer distinct() directamente con objeto, por lo que hay que pasar la lista de objeto a las id
            recetas_id = Ingrediente_Receta.objects.filter(ingrediente__in=ingredientes).values_list('receta', flat=True).distinct()
            recetas = []
            
            for id in recetas_id:   #Se crea el objeto receta a traves de su id
                receta = Receta.objects.get(pk=id)
                receta.num = 0 #Se inicializa el atributo num que indica la cantidad de ingredientes que coinciden
                # Recorre los ingredientes de cada receta
                # En caso que dicho ingrediente esté en la lista de ingredientes introducido suma 1
                receta.num += sum(1 for receta_ingr in receta.ingredientes.all() if receta_ingr.ingrediente in ingredientes)
                recetas.append(receta)
            
            recetas.sort(key=lambda x: x.num, reverse=True) #Ordena la receta por cantidad de coincidencias de mayor a menor

            # Mensaje indicando los ingredientes que busca
            if ingredientes:
                mensaje = "Resultados de "
                
                for ingrediente in ingredientes:
                    mensaje += ingrediente.nombre + ", "
                
                mensaje = mensaje[:-2]  #Borra los 2 último caracteres del string (, )
            
            else:
                mensaje = "No se han encontrado recetas"
            
            context = {
                'recetas': utils.paginator(request, recetas), 
                'mensaje_titulo': mensaje
            }
            
            # En caso de que sea post retorna a la lista de recetas
            return render(request, 'resultado_busqueda.html', context)
    else:
        formset = form()
        

    context = {
        'formset': formset
    }

    return render(request, 'busqueda_avanzada.html', context)


# Buscador del encabezado
@login_required
def resultado_busqueda(request):
    query = request.GET.get('name')

    try:    # Comprueba que haya una categoría con el nombre introducido
        categoria = Categoria.objects.get(nombre=query.capitalize())
        recetas = Receta.objects.filter(categoria=categoria)
    except ObjectDoesNotExist:  # Si no hay, obtiene las recetas que se llamen como se ha introducido en el buscador
        recetas = Receta.objects.filter(Q(titulo__icontains=query))

    if recetas:
        mensaje = "Resultados de " + query
    else:
        mensaje = 'No se ha encontrado ninguna receta con "' + query + '"'

    context = {
        'recetas': utils.paginator(request, recetas),
        'mensaje_titulo': mensaje
    }

    return render(request, 'resultado_busqueda.html', context)

# Resultado búsqueda por categoría
@login_required
def resultado_busqueda_categoria(request, c):
    categoria = get_object_or_404(Categoria, pk=c)
    recetas = Receta.objects.filter(categoria=c).order_by('-fecha')
    mensaje = "Resultados de " + categoria.nombre if recetas else 'No se ha encontrado ninguna receta de la categoría ' + categoria.nombre

    context = {
        'recetas': utils.paginator(request, recetas),
        'mensaje_titulo': mensaje
    }

    return render(request, 'resultado_busqueda.html', context)


#Pantalla de registro a la aplicacion
def registro(request):

    if request.method == "POST":
        registroUserForm = RegistroUserForm(request.POST)
        registroPerfilForm = RegistroPerfilForm(request.POST, request.FILES)
        
        if registroUserForm.is_valid() and registroPerfilForm.is_valid():
            username = registroUserForm.cleaned_data.get('username')
            password = registroUserForm.cleaned_data.get('password')
            password2 = registroUserForm.cleaned_data.get('password2')
            email = registroUserForm.cleaned_data.get('email')
            
            # Comprueba que no exista un usuario con el nombre de usuario o introducido, que las password coincidan y no sean numéricas
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists() and password == password2 and not password.isnumeric():
                user = registroUserForm.save()
                registroPerfilForm.save(user)
                do_login(request, user) #Accede a la aplicación
                return redirect('index')
            
            else:   # En caso de que haya algún error, comprueba cuales han sido para mostrarlo por pantalla
                if User.objects.filter(email=email).exists():
                    registroUserForm.add_error('email', 'Ya existe un usuario registrado con este email.')
                if password.isnumeric():
                    registroUserForm.add_error('password', 'Las contraseñas no pueden ser solo numérica.')
                if not password == password2:
                    registroUserForm.add_error('password', 'Las contraseñas no coinciden.')
                
    else:
        registroUserForm = RegistroUserForm()
        registroPerfilForm = RegistroPerfilForm()

    context = {
        'userForm': registroUserForm,
        'perfilForm': registroPerfilForm,
    }

    return render(request, 'registration/registro_perfil.html', context)


"""
    Funcionalidades
"""

#Elimina la cuenta logueada y redirecciona a la pantalla de logueo
@login_required
def eliminar_cuenta(request):
    request.user.perfil.delete()
    return redirect('login')


#Elimina la foto de perfil y redirecciona a pantalla de ajustes
@login_required
def eliminar_foto(request):
    request.user.perfil.set_imagen(None)
    return redirect('editar_perfil', username=request.user.username)


#Elimina una receta y redirecciona a pantalla principal
@login_required
def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.user == receta.usuario:  # Comprueba que la receta pertenezca al usuario logueado      
        receta.delete()
        
    return redirect('perfil', username=request.user.username)


#Pone una receta pública o privada según la que esté marcada
@login_required()
def publicar(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.user == receta.usuario:  # Comprueba que la receta pertenezca al usuario logueado
        receta.publicar()
    
    return redirect('receta', pk=pk)
    

"""
    FUNCIONES LLAMADAS CON AJAX
"""

# Guarda una receta que se pasa por parametro y se guarda en el usuario conectado
@login_required
def guardar(request):
    
    if request.method == 'GET':
        receta_id = request.GET['receta_id']
        receta = Receta.objects.get(id=receta_id)

        # En caso de que ya se tenga guardada, la quita de la lista de guardadas
        if Receta_Guardada.objects.filter(receta=receta).filter(usuario=request.user).exists():
            Receta_Guardada.objects.filter(receta=receta).filter(usuario=request.user).delete()
        else: # En caso contrario, la añade
            Receta_Guardada.objects.create(receta=receta, usuario=request.user)
        
        return HttpResponse()

# Valora una receta
@login_required
def valorar(request):
    
    if request.method == 'GET':
        receta = get_object_or_404(Receta, pk=request.GET['receta_id']) # Obtienes la receta por la id
        valoracion = request.GET['valoracion']

        #No tiene ya valoracion por el mismo usuario
        if not Valoracion.objects.filter(receta=receta).filter(usuario=request.user).exists():
            Valoracion.objects.create(valoracion=valoracion, receta=receta, usuario=request.user)   # Crea valoración
            receta.valoracion_media = utils.valoracion_media(receta)
            utils.add_notificacion(request.user, receta.usuario, "valoracion", receta)  # Crea notificación
            return HttpResponse(receta.valoracion_media)
        else:
            return HttpResponse('existe')

# Cuando se valora, a través del modal, porque un usuario ya habia valorado dicha receta
@login_required    
def valorar_seguro(request):

    if request.method == 'GET':
        receta = get_object_or_404(Receta, pk=request.GET['receta_id'])
        
        # Obtiene la valoración ya existente
        valoracion = Valoracion.objects.filter(receta=receta).filter(usuario=request.user).first()  # Obtiene la valoración ya existente
        valoracion.valoracion = request.GET['valoracion']
        valoracion.save()
        receta.valoracion_media = utils.valoracion_media(receta)
        utils.add_notificacion(request.user, receta.usuario, "valoracion", receta)  # Crea la notificación
        
        return HttpResponse(receta.valoracion_media)
    


# Un usuario envía una sugerencia de una categoría o unidad de medida
@login_required
def sugerencia(request):
    
    if request.method == "GET":

        # Busca si existe la sugerencia
        if Sugerencia.objects.filter(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia']).exists():
            sugerencia = Sugerencia.objects.filter(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia']).first()
            sugerencia.cantidad += 1    # Si esa sugerencia existe, suma 1 al campo cantidad para ver cuantos la han enviado en total
            sugerencia.save()
        else:   # Crea una nueva sugerencia
            Sugerencia.objects.create(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia'])
        
        return HttpResponse()
        

@login_required
def hay_notificaciones(request):

    # Comprueba que sea GET y que el usuario tenga notificaciones sin ver
    if request.method == "GET" and Notificacion.objects.filter(usuario_destino=request.user).filter(visto=False).exists():
        return HttpResponse("si-notificacion")
        
    return HttpResponse()


@login_required
def seguir_dejar(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if not request.user == usuario:
        usuario.perfil.seguir(request.user.perfil)

        if not request.user.perfil in usuario.perfil.seguidores.all():  # En caso de que no lo siga
            utils.add_notificacion(request.user, usuario, "siguiendo")
            return HttpResponse("siguiendo")
        else:   
            return HttpResponse("dejado")
    
    raise Http404   # Si el usuario es el mismo => error404

def error_404(request, exception):
        return render(request,'404.html', {})
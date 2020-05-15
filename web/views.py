from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .forms import *
from . import utils

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

#Cambiar pass
from django.contrib.auth import update_session_auth_hash
#from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

#Fromset
from django.forms import modelformset_factory, formset_factory

#Contains
from django.db.models import Q

from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist


# Pantalla principal
@login_required
def index(request):

    try:    # Comprueba que el usuario tiene un perfil
        request.user.perfil
    except ObjectDoesNotExist:
        logout(request)
        return redirect('login')

    recetas = Receta.objects.filter(publico=True).order_by('-fecha')    #Todas las recetas
    
    for receta in recetas:  # Añade la valoración media a cada receta
        receta.valoracion_media = utils.valoracion_media(receta)

    #Paginación
    obj_pagina = utils.paginator(request, recetas)

    context = {
        'recetas': obj_pagina,
        'mensaje_vacio': "No hay recetas"
    }
    
    return render(request, 'index.html', context)


# Vista de una receta creada
@login_required
def receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)  # Obtiene la receta
        
    # Formulario respuesta a un comentario
    if request.method == 'POST' and 'comentario-respuesta' in request.POST:
        respuestaForm = RespuestaForm(request.POST)

        if respuestaForm.is_valid():
            texto = respuestaForm.cleaned_data['texto']
            padre = Comentario.objects.get(
                pk=int(request.POST['comentario-respuesta']))
            Comentario.objects.create(
                texto=texto, receta=receta, usuario=request.user, comentario_respuesta=padre)
            

    # Formulario escribir comentario
    if request.method == "POST" and 'comentario' in request.POST:  # En caso de que escriba un comentario
        comentarioForm = ComentarioForm(request.POST)

        if comentarioForm.is_valid():
            comentario = comentarioForm.save(commit=False)  # Guarda el texto
            comentario.usuario = request.user  # Añade el usuario
            comentario.receta = Receta.objects.get(pk=pk)  # Le añade la receta
            comentario.save()

    comentarioFrom = ComentarioForm()
    valoracionForm = ValoracionForm()
    respuestaForm = RespuestaForm()
    
    # Añade a la receta la valoración media
    receta.valoracion_media = utils.valoracion_media(receta)
    
    context = {'receta': receta, 'valoracionForm': valoracionForm,
               'comentarioForm': comentarioFrom, 'respuestaForm': respuestaForm}

    return render(request, 'receta.html', context)


@login_required
def nueva_receta(request):

    formsetPasoFactory = modelformset_factory(Paso, form=PasoFormset, extra=1)
    formsetIngredienteFactory = modelformset_factory(Ingrediente_Receta, form=IngredienteFormset, extra=1)

    if request.method == 'POST':
        
        if 'sugerencia' in request.POST:    # Si envía una sugerencia
            formSugerencia = SugForm(request.POST)
            
            if formSugerencia.is_valid():
                formSugerencia.save()
                return redirect('nueva_receta')
            else:   # Siempre es válido, se pone para que no hagas las siguientes operaciones
                return redirect('nueva_receta')

        formReceta = RecetaForm(request.POST, request.FILES)
        formset_paso = formsetPasoFactory(request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(request.POST, prefix='ingrediente')

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            # Receta (básicos)
            receta = formReceta.save(commit=False)
            
            if request.POST.__contains__('publico'): #Comprueba que se pulse el botón publicar
                receta.publico = True

            receta.usuario = request.user
            receta.save()

            # Ingredientes
            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                rel_ingrediente = formIngrediente.save(commit=False)
                formIngrediente = formIngrediente.cleaned_data
                
                # Comprueba que exista el ingrediente
                if Ingrediente.objects.filter(nombre=formIngrediente['ingrediente']).exists():
                    rel_ingrediente.ingrediente = Ingrediente.objects.get(nombre=formIngrediente['ingrediente'])
                else:   # Si no, crea el ingrediente
                    nombre = formIngrediente['ingrediente']
                    instancia = Ingrediente.objects.create(nombre=nombre)
                    rel_ingrediente.ingrediente = instancia

                rel_ingrediente.receta = receta
                rel_ingrediente.save()

            # Pasos
            pos = 1
            
            for formPaso in formset_paso:   #Bucle todos los pasos
                paso = formPaso.save(commit=False)
                paso.receta = receta
                paso.posicion = pos
                paso.save()
                pos += 1

            return redirect('receta', pk=receta.pk)

        else:
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
        formSugerencia = SugForm()

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
    
    formsetPasoFactory = modelformset_factory(Paso, form=PasoFormset, extra=0)
    formsetIngredienteFactory = modelformset_factory(Ingrediente_Receta, form=IngredienteEditFormset, extra=0)

    if request.method == 'POST':
        if 'sugerencia' in request.POST:    # Si envía una sugerencia
            formSugerencia = SugForm(request.POST)
            
            if formSugerencia.is_valid():
                formSugerencia.save()
                return redirect('editar_receta', pk=pk)
            else:   # Siempre es válido, se pone para que no hagas las siguientes operaciones
                return redirect('editar_receta')

        formReceta = RecetaForm(request.POST, request.FILES, instance=receta)
        formset_paso = formsetPasoFactory(request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(request.POST, prefix='ingrediente')

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            # Receta (básicos)
            receta = formReceta.save(commit=False)
            
            if request.POST.__contains__('publico'): #Comprueba que se pulse el botón publicar
                receta.publico = True

            receta.usuario = request.user
            receta.save()

            # Ingredientes
            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                rel_ingrediente = formIngrediente.save(commit=False)
                formIngrediente = formIngrediente.cleaned_data
                
                # Comprueba que exista el ingrediente
                if Ingrediente.objects.filter(nombre=formIngrediente['ingrediente']).exists():
                    rel_ingrediente.ingrediente = Ingrediente.objects.get(nombre=formIngrediente['ingrediente'])
                else:   # Si no, crea el ingrediente
                    nombre = formIngrediente['ingrediente']
                    instancia = Ingrediente.objects.create(nombre=nombre)
                    rel_ingrediente.ingrediente = instancia

                rel_ingrediente.receta = receta
                rel_ingrediente.save()

            # Pasos
            pos = 1
            
            for formPaso in formset_paso:   #Bucle todos los pasos
                paso = formPaso.save(commit=False)
                paso.receta = receta
                paso.posicion = pos
                paso.save()
                pos += 1

            return redirect('receta', pk=receta.pk)
        else:
            # En caso de que no sea válido el formulario, muestra los errores
            # Nunca va a dar la situación porque o es requerido, que no 
            # se envía el formulario en caso de que no se introduzca los datos
            # o tiene máximo de caracteres, que no se permite introducir más
            # en el campo de texto
            pass

    else:   # Si no es POST
        formReceta = RecetaForm(instance=receta)
        formset_paso = formsetPasoFactory(queryset=Paso.objects.filter(receta=receta).order_by('posicion'), prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(queryset=Ingrediente_Receta.objects.filter(receta=receta), prefix='ingrediente')
        formSugerencia = SugForm()

        # Cambia que donde se almacena el id del ingrediente, por el nombre de dicho
        # para que en el formulario se muestre el nombre del insgrediente en vez del id
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
    
    for receta in recetas:  # Añade la valoración media a cada receta
        receta.valoracion_media = utils.valoracion_media(receta)
    
    #Paginación
    obj_pagina = utils.paginator(request, recetas)

    context = {
        'usuario': user,
        'recetas': obj_pagina,
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
    
    # Obtiene una lista de id de recetas que el usuario tiene guardada y ordenada por fecha
    lista_recetas = Receta_Guardada.objects.filter(usuario=user).values_list('receta', flat=True).order_by('-fecha') 
    recetas = []
    
    for id_receta in lista_recetas:
        receta = Receta.objects.get(pk=id_receta)
        receta.valoracion_media = utils.valoracion_media(receta)
        recetas.append(receta)

    mensaje_vacio = "Aún no tienes ninguna receta guardada"  
    

    context = {
        'usuario': user,
        'recetas': utils.paginator(request, recetas),
        'mensaje_vacio': mensaje_vacio,
        'lista_es_receta': True,
    }

    return render(request, 'perfil.html', context)


#Vista de perfil con la lista de seguidores
@login_required
def seguidores(request, username):
    user = get_object_or_404(User, username=username)
    
    # Obtiene la lista de los usuarios a los que sigue
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    
    seguidores = user.perfil.seguidores.all()   # Obtiene la lista seguidores

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
    
    siguiendo = Perfil.objects.filter(seguidores=user.perfil)   # Obtiene la lista de usuarios siguiendo

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
            cd = form.cleaned_data
            request.user.first_name = cd['nombre']
            request.user.last_name = cd['apellido']
            request.user.perfil.descripcion = cd['descripcion']
            request.user.perfil.set_imagen(cd['imagen_perfil'])
            request.user.save()
            request.user.perfil.save()
        else:
            # No puede haber errores
            pass
    else:

        form = EditarPerfilForm(initial={
                'nombre': request.user.first_name,
                'apellido': request.user.last_name,
                'descripcion': request.user.perfil.descripcion,
            })

    return render(request, 'editar_perfil.html', {'form': form})


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
        print("-"*10)
        print(form)     

    context = {
        'form': form
    }

    return render(request, 'editar_pass.html', context)


#Busqueda avanzada de recetas 
@login_required
def busqueda_avanzada(request):
    form = formset_factory(form=BusquedaAvanzadaForm, extra=1)
    
    if request.method == 'POST':
        formset = form(request.POST)
        ingredientes = []

        if formset.is_valid():
            
            for form in formset:   #Por cada input del formulario, obtiene el objeto ingrediente
                try:
                    ingrediente = Ingrediente.objects.get(nombre=form.cleaned_data['ingrediente']) #Obtiene el objeto ingrediente a través del nombre
                    if not ingrediente in ingredientes: #Comprueba que no esté en la lista para que no haya repetidos
                        ingredientes.append(ingrediente)
                except Ingrediente.DoesNotExist:    #Excepción en caso de que no exista un ingrediente con el nombre introducido
                    pass    # No hace nada, lo deja pasar
            
            #Obtiene la lista de recetas filtrando por ingrediente y sin obtener repetidos
            #Sqlite no soporta hacer distinct() directamente con objeto, por lo que hay que pasar la lista de objeto a las id
            recetas_id = Ingrediente_Receta.objects.filter(ingrediente__in=ingredientes).values_list('receta', flat=True).distinct()
            recetas = []
            
            for id in recetas_id:   #Se crea el objeto receta a traves de su id
                receta = Receta.objects.get(pk=id)
                receta.num = 0 #Se inicializa el atributo num que indica la cantidad de ingredientes que coinciden

                for receta_ingr in receta.ingredientes.all():   #Recorre los ingredientes de cada receta
                    if receta_ingr.ingrediente in ingredientes: 
                        receta.num = receta.num + 1 #En caso que dicho ingrediente esté en la lista de ingredientes introducido suma 1
                
                recetas.append(receta)
            
            recetas.sort(key=lambda x: x.num, reverse=True) #Ordena la receta por cantidad de coincidencias de mayor a menor

            # Mensaje indicando los ingredientes que busca
            mensaje = "Resultados de "
            
            for ingrediente in ingredientes:
                mensaje += ingrediente.nombre + ", "
            
            mensaje = mensaje[:-2]  #Borra los 2 último caracteres del string

            context = {
                'recetas': utils.paginator(request, recetas), 
                'mensaje_titulo': mensaje if len(recetas) > 0 else "",
                'mensaje_vacio': "No se han encontrado recetas"
            }
            
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

    context = {
        'recetas': utils.paginator(request, recetas),
        'mensaje_titulo': "Resultados de " + query if len(recetas) > 0 else "",
        'mensaje_vacio': 'No se ha encontrado ninguna receta con "' + query + '"',
    }

    return render(request, 'resultado_busqueda.html', context)



#Pantalla de registro a la aplicacion
def registro(request):

    if request.method == "POST":
        registroUserForm = RegistroUserForm(request.POST)
        registroPerfilForm = RegistroPerfilForm(request.POST, request.FILES)

        if registroUserForm.is_valid() and registroPerfilForm.is_valid():
            
            # Obtiene todos los datos
            username = registroUserForm.cleaned_data.get('username')
            password = registroUserForm.cleaned_data.get('password')
            password2 = registroUserForm.cleaned_data.get('password2')
            email = registroUserForm.cleaned_data.get('email')
            nombre = registroUserForm.cleaned_data.get('first_name')
            apellido = registroUserForm.cleaned_data.get('last_name')
            descripcion = registroPerfilForm.cleaned_data.get('descripcion')
            imagen = registroPerfilForm.cleaned_data.get('imagen_perfil')
            
            
            # Comprueba que no exista un usuario con el nombre de usuario introducido
            if not User.objects.filter(username=username).exists():

                # Comprueba que no exista un usuario con el email introducido
                if not User.objects.filter(email=email).exists():

                    if password == password2:

                        if not password.isnumeric():
                            user = registroUserForm.save(commit=False)
                            user.set_password(password)
                            user.first_name = nombre
                            user.last_name = apellido
                            user.email = email
                            user.save() #Guarda el objeto user

                            perfil = Perfil(usuario=user)
                            perfil.descripcion = descripcion
                            perfil.set_imagen(imagen)
                            perfil.save()   #Guarda el perfil de dicho usuario
                            do_login(request, user) #Accede a la aplicación
                            return redirect('index')
                        else:
                            registroUserForm.add_error('password', 'Las contraseñas no pueden ser solo numérica.')
                    else:
                        registroUserForm.add_error('password', 'Las contraseñas no coinciden.')
                else:
                    registroUserForm.add_error('email', 'Ya existe un usuario registrado con este email.')

    else:
        registroUserForm = RegistroUserForm()
        registroPerfilForm = RegistroPerfilForm()

    context = {
        'userForm': registroUserForm,
        'perfilForm': registroPerfilForm,
    }

    return render(request, 'registration/registro_perfil.html', context)


#Elimina la cuenta logueada y redirecciona a la pantalla de logueo
@login_required
def eliminar_cuenta(request):
    request.user.delete()
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


#Pone una receta pública
@login_required()
def publicar(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.user == receta.usuario:  # Comprueba que la receta pertenezca al usuario logueado
        receta.publicar()
        return redirect('receta', pk=pk)


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
        return HttpResponse('success')
    

# Valora una receta
@login_required
def valorar(request):
    
    if request.method == 'GET':
        receta_id = request.GET['receta_id']
        receta = get_object_or_404(Receta, pk=receta_id)
        valoracion = request.GET['valoracion']

        #No tiene ya valoracion
        if not Valoracion.objects.filter(receta=receta).filter(usuario=request.user).exists():
            Valoracion.objects.create(valoracion=valoracion, receta=receta, usuario=request.user)
            receta.valoracion_media = utils.valoracion_media(receta)
            return HttpResponse(receta.valoracion_media)
        else:
            return HttpResponse('existe')

# Cuando se valora, a través del modal
@login_required    
def valorar_seguro(request):

    if request.method == 'GET':
        receta_id = request.GET['receta_id']
        receta = get_object_or_404(Receta, pk=receta_id)
        puntos = request.GET['valoracion']
        
        # Obtiene la valoración ya existente
        valoracion = Valoracion.objects.filter(receta=receta).filter(usuario=request.user).first()
        valoracion.valoracion = puntos
        valoracion.save()
        receta.valoracion_media = utils.valoracion_media(receta)
        
        return HttpResponse(receta.valoracion_media)
    
    return HttpResponse("unsuccessful")


@login_required
def sugerencia(request):
    
    if request.method == "GET":
        # Busca si existe la sugerencia
        if Sugerencia.objects.filter(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia']).exists():
            sugerencia = Sugerencia.objects.filter(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia']).first()
            sugerencia.cantidad += 1
            sugerencia.save()
        else:
            Sugerencia.objects.create(tipo=request.GET['categoria'], sugerencia=request.GET['sugerencia'])
        
        return HttpResponse()

    return HttpResponse("unsuccessful")

@login_required
def seguir(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if not request.user == usuario:
        usuario.perfil.add_seguidor(request.user.perfil)
        return redirect('perfil', username=usuario.username)


@login_required
def dejar_seguir(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if not request.user == usuario:
        usuario.perfil.dejar_seguir(request.user.perfil)
        return redirect('perfil', username=usuario.username)



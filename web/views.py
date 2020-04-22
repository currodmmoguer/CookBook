from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

#Cambiar pass
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

#Fromset
from django.forms import modelformset_factory, formset_factory

#Contains
from django.db.models import Q

from django.http import HttpResponse

#Paginacion
from django.core.paginator import Paginator

# Pantalla principal
@login_required
def index(request):
    recetas = Receta.objects.filter(publico=True).order_by('-fecha')    #Todas las recetas
    
    #Para mostrar las recetas de los usuarios que sigue
    siguiendo = Perfil.objects.filter(seguidores=request.user.perfil)
    recetas_sigue = Receta.objects.filter(
        usuario__perfil__in=siguiendo).filter(publico=True).order_by('-fecha')
    
    for r in recetas:  # Añade la valoración media a cada receta
        r.valoracion_media = Valoracion.objects.filter(
            receta=r).aggregate(Avg('valoracion'))['valoracion__avg']

    #Paginación
    paginator = Paginator(recetas, 10)
    num_pagina = request.GET.get('page')
    obj_pagina = paginator.get_page(num_pagina)

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
    if request.method == 'POST' and 'respuesta' in request.POST:
        respuestaForm = RespuestaForm(request.POST)

        if respuestaForm.is_valid():
            texto = respuestaForm.cleaned_data['respuesta']
            padre = Comentario.objects.get(
                pk=int(respuestaForm.cleaned_data['comentario']))
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

    # Formulario valoración
    if request.method == "POST" and 'valoracion' in request.POST:  # En caso de que seauna valoración
        valoracionForm = ValoracionForm(request.POST)
        
        #Comprueba que sea valido y que no haya valorado ya
        if valoracionForm.is_valid() and not Valoracion.objects.filter(receta=Receta.objects.get(pk=pk)).filter(usuario=request.user).exists():
            valoracion = valoracionForm.save(
                request.user, Receta.objects.get(pk=pk))
        else:
            print('Errors: %s' % valoracionForm.errors.as_text())

    comentarioFrom = ComentarioForm()
    valoracionForm = ValoracionForm()
    respuestaForm = RespuestaForm()

    context = {'receta': receta, 'valoracionForm': valoracionForm,
               'comentarioForm': comentarioFrom, 'respuestaForm': respuestaForm, 'valoracion_media': Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']}

    return render(request, 'receta.html', context)

#Pantalla para editar una receta
@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    formsetPasoFactory = modelformset_factory(
        Paso, form=PasoFormset, extra=1)
    formsetIngredienteFactory = modelformset_factory(
        Ingrediente_Receta, form=IngredienteFormset, extra=1)

    formset_paso = formsetPasoFactory(
            queryset=Paso.objects.filter(receta=receta).order_by('posicion'), prefix='paso')
    formset_ingrediente = formsetIngredienteFactory(
            queryset=Ingrediente_Receta.objects.filter(receta=receta), prefix='ingrediente')

    context = {'receta': receta, 'categorias': Categoria.objects.all(),
                'formsetPaso': formset_paso, 'formsetIngrediente': formset_ingrediente}

    return render(request, 'editar_receta.html', context)


#Perfil de un usuario
@login_required
def perfil(request, username):
    user = get_object_or_404(User, username=username)
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    """if request.user == user:
        recetas = user.recetas.all().order_by('-fecha')
        mensaje_vacio = "Aún no tienes ninguna receta creada"
    else:
        recetas = user.recetas.filter(publico=True).order_by('-fecha')
        mensaje_vacio = username + " no tiene ninguna receta creada"
    
    for r in recetas:  # Añade la valoración media a cada receta
        r.valoracion_media = Valoracion.objects.filter(
            receta=r).aggregate(Avg('valoracion'))['valoracion__avg']
    """
    recetas = user.recetas.all().order_by('-fecha')
    context = {'usuario': user, 'recetas': recetas, 'mensaje_vacio': "mensaje_vacio"}
    return render(request, 'perfil-general.html', context)




#Vista del perfil con las recetas guardadas
@login_required
def recetas_guardadas(request, username):
    user = get_object_or_404(User, username=username)
    
    if user == request.user:    #Comprueba que el perfil es el mismo que el usuario logueado
        recetas = request.user.recetas_guardadas.all()
        mensaje_vacio = "Aún no tienes ninguna receta guardada"
    else:
        return redirect('perfil', username=username)

    context = {'usuario': user, 'recetas': recetas, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-general.html', context)


#Vista de perfil con la lista de seguidores
@login_required
def seguidores(request, username):
    user = get_object_or_404(User, username=username)
    mensaje_vacio = username + " no tiene seguidores."
    seguidores = user.perfil.seguidores.all()
    context = {'usuario': user, 'lista_usuarios': seguidores, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-usuarios.html', context)


#Vista de perfil con la lista de usuarios que sigue
@login_required
def siguiendo(request, username):
    user = get_object_or_404(User, username=username)
    mensaje_vacio = username + " no sigue a nadie."
    siguiendo = Perfil.objects.filter(seguidores=user.perfil)
    context = {'usuario': user, 'lista_usuarios': siguiendo, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-usuarios.html', context)

"""
# Pantalla de acceso
def login_view(request):
    context = {}
    print("Aquiii")

    if request.method == "POST":
        loginForm = LoginForm(request.POST)

        if 'login' in request.POST:
            print("Post")
            if loginForm.is_valid():
                print("Valido")
                username = loginForm.cleaned_data['username']
                password = loginForm.cleaned_data['password']
                usuario = authenticate(username=username, password=password)
                if usuario is not None:
                    do_login(request, usuario)
                    return redirect('index')
                else:
                    print("Aqui")
                    loginForm.add_error('data', 'Has introducido datos erroneros. Vuelve a intentarlo')
                    context['form'] = loginForm
                    context['mensaje_error'] = "Has introducido datos erroneros. Vuelve a intentarlo"
    else:
        context = {
            'form': LoginForm(),
            'mensaje_error': ""
        }

    print(context)

    return render(request, 'registration/login.html', context)"""




#Pantalla de registro a la aplicacion
def registro(request):

    if request.method == "POST":
        registroUserForm = RegistroUserForm(request.POST)
        registroPerfilForm = RegistroPerfilForm(request.POST, request.FILES)

        if registroUserForm.is_valid() and registroPerfilForm.is_valid():
            username = registroUserForm.cleaned_data.get('username')
            password = registroUserForm.cleaned_data.get('password')
            email = registroUserForm.cleaned_data.get('email')
            nombre = registroUserForm.cleaned_data.get('first_name')
            apellido = registroUserForm.cleaned_data.get('last_name')
            descripcion = registroPerfilForm.cleaned_data.get('descripcion')
            imagen = registroPerfilForm.cleaned_data.get('imagen_perfil')
            
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = registroUserForm.save(commit=False)
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
                    registroUserForm.add_error('email', 'Ya existe un usuario registrado con este email.')
        else:
            print(registroUserForm.errors.as_text())
            print(registroPerfilForm.errors.as_text())

    else:
        registroUserForm = RegistroUserForm()
        registroPerfilForm = RegistroPerfilForm()

    context = {
        'userForm': registroUserForm,
        'perfilForm': registroPerfilForm,
    }

    return render(request, 'registration/registro_perfil.html', context)

def sugerencia(request):
    print("entra")


@login_required
def nueva_receta(request):

    formsetPasoFactory = modelformset_factory(
        Paso, form=PasoFormset, extra=1)
    formsetIngredienteFactory = modelformset_factory(
        Ingrediente_Receta, form=IngredienteFormset, extra=1)


    if request.method == 'POST':

        if 'sugerencia' in request.POST:
            formSugerencia = SugForm(request.POST)
            print(formSugerencia.data)
            if formSugerencia.is_valid():
                print(formSugerencia.cleaned_data)
                return HttpResponse("Se ha enviado tu sugerencia")
            else:
                print(formSugerencia.errors.as_text())
                print("La sugerencia no vale")
                return redirect('nueva_receta')

        formReceta = RecetaForm(request.POST, request.FILES)
        formset_paso = formsetPasoFactory(
            request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(
            request.POST, prefix='ingrediente')

        

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            receta = formReceta.save(commit=False)
            
            if request.POST.get('publico'): #Comprueba que se pulse el botón publicar
                receta.publico = True

            receta.usuario = request.user
            receta.save()

            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                rel_ingrediente = formIngrediente.save(commit=False)
                formIngrediente = formIngrediente.cleaned_data


                if Ingrediente.objects.filter(nombre=formIngrediente['ingrediente']).exists():
                    rel_ingrediente.ingrediente = Ingrediente.objects.get(nombre=formIngrediente['ingrediente'])
                else:
                    nombre = formIngrediente['ingrediente']
                    instancia = Ingrediente.objects.create(nombre=nombre)
                    rel_ingrediente.ingrediente = instancia

                rel_ingrediente.receta = receta
                rel_ingrediente.save()

            pos = 1
            for formPaso in formset_paso:   #Bucle todos los pasos
                paso = formPaso.save(commit=False)
                print(formPaso.cleaned_data)
                paso.receta = receta
                paso.posicion = pos
                paso.save()
                pos += 1

            return redirect('receta', pk=receta.pk)

        else:
            print("No es valido")
            print(formReceta.errors.as_text())
            print(formset_paso.errors)
            print(formset_ingrediente.errors)

    else:
        formReceta = RecetaForm()
        formset_paso = formsetPasoFactory(
            queryset=Paso.objects.none(), prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(
            queryset=Ingrediente.objects.none(), prefix='ingrediente')

    context = {
        'formReceta': formReceta,
        'formsetIngrediente': formset_ingrediente,
        'formsetPaso': formset_paso,
        'categorias': Categoria.objects.all(),
        'unidades': Unidad_medida.objects.all(),
        'formSugerencia': SugForm(),
    }

    return render(request, 'nueva-receta.html', context)




#Formulario para editar datos del perfil
@login_required
def editar_perfil(request, username):

    form = EditarPerfilForm()
    
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES)
        print(form.data)
        if form.is_valid():
            print("valid")
            cd = form.cleaned_data
            if not cd['nombre'] == '':
                request.user.first_name = cd['nombre']
            if not cd['apellido'] == '':
                request.user.last_name = cd['apellido']
            if not cd['descripcion'] == '':
                print("entra")
                request.user.perfil.descripcion = cd['descripcion']
            if not cd['imagen_perfil'] == None:
                request.user.perfil.set_imagen(cd['imagen_perfil'])
            request.user.save()
            request.user.perfil.save()
        else:
            print(form.errors.as_text())

    return render(request, 'editar_perfil.html', {'form': form})


#Formulario para cambiar la contraseña de la cuenta
@login_required
def editar_pass(request, username):
    user = get_object_or_404(User, username=request.user.get_username())

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Se ha actualizado la contraseña correctamente')
            return redirect('editar_pass', username=username)
        else:
            messages.error(request, 'Error al cambiar la contraseña')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'editar_pass.html', {'usuario': user, 'form': form})


#Pone una receta pública
def publicar(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    receta.publicar()
    return redirect('receta', pk=pk)


# Guarda una receta que se pasa por parametro y se guarda en el usuario conectado
@login_required
def guardar(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    receta.guardar(request.user)
    return redirect('index')


@login_required
def seguir(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.perfil.seguidores.add(request.user.perfil)
    return redirect('perfil', username=usuario.username)


@login_required
def dejar_seguir(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.perfil.dejar_seguir(request.user.perfil)
    return redirect('perfil', username=usuario.username)


#Pantalla para cambiar la contraseña de la cuenta
@login_required
def cambiar_pass(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('cambiar_pass')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, '')


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
    if request.user == receta.usuario:
        print("Entra")
        receta.delete()
        return redirect('index')




#Busqueda avanzada de recetas 
@login_required
def busqueda_avanzada(request):
    print("funcion")
    
    form = formset_factory(form=BusquedaAvanzadaForm, extra=1)
    formset = form()

    if request.method == 'POST':
        formset = form(request.POST)
        ingredientes = []

        if formset.is_valid():
            
            for forma in formset:
                try:
                    ingredientes.append(Ingrediente.objects.get(nombre=forma.cleaned_data['ingrediente']))
                except Ingrediente.DoesNotExist:
                    pass
            
            recetas_id = Ingrediente_Receta.objects.filter(ingrediente__in=ingredientes).values_list('receta', flat=True).distinct()
            recetas = []
            
            for id in recetas_id:
                receta = Receta.objects.get(pk=id)
                receta.num = 0

                for receta_ingr in receta.ingredientes.all():
                    if receta_ingr.ingrediente in ingredientes:
                        receta.num = receta.num + 1
                
                recetas.append(receta)
            
            recetas.sort(key=lambda x: x.num, reverse=True)
            
            return render(request, 'resultado_busqueda.html', {'recetas': recetas})

    context = {
        'formset': formset
    }

    return render(request, 'busqueda_avanzada.html', context)


@login_required
def resultado_busqueda(request):
    print(request.GET)
    query = request.GET.get('name')
    recetas = Receta.objects.filter(Q(titulo__icontains=query))
    print(recetas)
    context = {
        'recetas': receta,
        'palabra': query,
        'mensaje_vacio': 'No se ha encontrado ninguna receta con "' + query + '"'
    }
    return render(request, 'resultado_busqueda.html', context)

def rueba(request):
    print("Enrrra")
    
    return HttpResponse("Erorrr")

def error_404(request, excepction):
    return render(request, 'error_404.html')



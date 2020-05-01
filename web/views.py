from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .forms import *
from .utils import *

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

from django.core.exceptions import ObjectDoesNotExist


# Pantalla principal
@login_required
def index(request):
    try:
        request.user.perfil
    except ObjectDoesNotExist:
        #Falta mostrar mensaje
        return redirect('login')

    recetas = Receta.objects.filter(publico=True).order_by('-fecha')    #Todas las recetas
    
    #if request.method == "GET" and 'guardar' in request.GET:
     #   print(request.GET.keys())
    
    #Para mostrar las recetas de los usuarios que sigue
    siguiendo = Perfil.objects.filter(seguidores=request.user.perfil)
    recetas_sigue = Receta.objects.filter(
        usuario__perfil__in=siguiendo).filter(publico=True).order_by('-fecha')
    
    for r in recetas:  # Añade la valoración media a cada receta
        r.valoracion_media = Valoracion.objects.filter(
            receta=r).aggregate(Avg('valoracion'))['valoracion__avg']

    #Paginación
    obj_pagina = paginator(request, recetas)

    context = {
        'recetas': obj_pagina,
        'mensaje_vacio': "No hay recetas"
    }
    

    return render(request, 'index.html', context)


# Vista de una receta creada
@login_required
def receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)  # Obtiene la receta

    if request.method == "GET" and 'guardar' in request.GET:
        receta.guardar(request.user)
        
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
    receta.valoracion_media = Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
    context = {'receta': receta, 'valoracionForm': valoracionForm,
               'comentarioForm': comentarioFrom, 'respuestaForm': respuestaForm}

    return render(request, 'receta.html', context)



@login_required
def nueva_receta(request):

    formsetPasoFactory = modelformset_factory(
        Paso, form=PasoFormset, extra=1)
    formsetIngredienteFactory = modelformset_factory(
        Ingrediente_Receta, form=IngredienteFormset, extra=1)


    if request.method == 'POST':
        
        if 'sugerencia' in request.POST:
            formSugerencia = SugForm(request.POST)
            
            if formSugerencia.is_valid():
                formSugerencia.save()
                return redirect('nueva_receta')
            else:
                return redirect('nueva_receta')

        formReceta = RecetaForm(request.POST, request.FILES)
        formset_paso = formsetPasoFactory(
            request.POST, request.FILES, prefix='paso')
        formset_ingrediente = formsetIngredienteFactory(
            request.POST, prefix='ingrediente')

        if formReceta.is_valid() and formset_ingrediente.is_valid() and formset_paso.is_valid():
            receta = formReceta.save(commit=False)
            
            if request.POST.__contains__('publico'): #Comprueba que se pulse el botón publicar
                receta.publico = True

            receta.usuario = request.user
            receta.save()

            print("Ingredientes")
            print(formset_ingrediente.cleaned_data)
            for formIngrediente in formset_ingrediente: #Bucle todos los ingredientes
                rel_ingrediente = formIngrediente.save(commit=False)
                formIngrediente = formIngrediente.cleaned_data
                print(formIngrediente)
                if Ingrediente.objects.filter(nombre=formIngrediente['ingrediente']).exists():
                    rel_ingrediente.ingrediente = Ingrediente.objects.get(nombre=formIngrediente['ingrediente'])
                else:
                    nombre = formIngrediente['ingrediente']
                    instancia = Ingrediente.objects.create(nombre=nombre)
                    rel_ingrediente.ingrediente = instancia

                rel_ingrediente.receta = receta
                rel_ingrediente.save()

            pos = 1
            print("Pasos")
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


#Pantalla para editar una receta
@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    formsetPasoFactory = modelformset_factory(
        Paso, form=PasoFormset, extra=0)
    formsetIngredienteFactory = modelformset_factory(
        Ingrediente_Receta, form=IngredienteEditFormset, extra=0)

    formset_paso = formsetPasoFactory(
            queryset=Paso.objects.filter(receta=receta).order_by('posicion'), prefix='paso')
    formset_ingrediente = formsetIngredienteFactory(
            queryset=Ingrediente_Receta.objects.filter(receta=receta), prefix='ingrediente')
    
        

    for ingrediente in formset_ingrediente:
        id_ingrediente = ingrediente.__dict__['initial']['ingrediente']
        nombre_ingrediente = Ingrediente.objects.get(id=id_ingrediente).nombre
        ingrediente.__dict__['initial']['ingrediente'] = nombre_ingrediente

    context = {'receta': receta, 'categorias': Categoria.objects.all(),
                'formsetPaso': formset_paso, 'formsetIngrediente': formset_ingrediente}

    return render(request, 'editar-receta.html', context)


#Perfil de un usuario
@login_required
def perfil(request, username):
    user = get_object_or_404(User, username=username)
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    
    if request.user == user:
        recetas = user.recetas.all().order_by('-fecha')
        mensaje_vacio = "Aún no tienes ninguna receta creada"
    else:
        recetas = user.recetas.filter(publico=True).order_by('-fecha')
        mensaje_vacio = username + " no tiene ninguna receta creada"
    
    for r in recetas:  # Añade la valoración media a cada receta
        r.valoracion_media = Valoracion.objects.filter(
            receta=r).aggregate(Avg('valoracion'))['valoracion__avg']
    
    
    context = {'usuario': user, 'recetas': recetas, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-general.html', context)




#Vista del perfil con las recetas guardadas
@login_required
def recetas_guardadas(request, username):
    user = get_object_or_404(User, username=username)
    
    if not user == request.user:    #Comprueba que el perfil es el mismo que el usuario logueado
        return redirect('perfil', username=username)
    
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    lista_recetas = Receta_Guardada.objects.filter(usuario=user).values_list('receta', flat=True).order_by('-fecha') 
    recetas = []
    for receta in lista_recetas:
        recetas.append(Receta.objects.get(pk=receta))

    mensaje_vacio = "Aún no tienes ninguna receta guardada"  
    context = {'usuario': user, 'recetas': recetas, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-general.html', context)


#Vista de perfil con la lista de seguidores
@login_required
def seguidores(request, username):
    user = get_object_or_404(User, username=username)
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    if user == request.user:
        mensaje_vacio = "Aún no tienes seguidores"
    else:
        mensaje_vacio = username + " no tiene seguidores"
    seguidores = user.perfil.seguidores.all()
    context = {'usuario': user, 'lista_usuarios': seguidores, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-usuarios.html', context)


#Vista de perfil con la lista de usuarios que sigue
@login_required
def siguiendo(request, username):
    user = get_object_or_404(User, username=username)
    user.perfil.total_siguiendo = Perfil.objects.filter(seguidores=user.perfil).count()
    
    if user == request.user:
        mensaje_vacio = "Aún no sigues a nadie"
    else:
        mensaje_vacio = username + " no sigue a nadie"

    siguiendo = Perfil.objects.filter(seguidores=user.perfil)
    context = {'usuario': user, 'lista_usuarios': siguiendo, 'mensaje_vacio': mensaje_vacio}
    return render(request, 'perfil-usuarios.html', context)



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
    print("entra en sugerencia")







#Formulario para editar datos del perfil
@login_required
def editar_perfil(request, username):

    form = EditarPerfilForm()
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES)
        
        if form.is_valid():
            print(form.cleaned_data)
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
def guardarr(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    rg = Receta_Guardada(receta=receta, usuario=request.user)
    rg.save()
    return redirect('index')

@login_required
def guardar(request):
    
    if request.method == 'GET':
        receta_id = request.GET['receta_id']
        receta = Receta.objects.get(id=receta_id)
        if Receta_Guardada.objects.filter(receta=receta).filter(usuario=request.user).exists():
            Receta_Guardada.objects.filter(receta=receta).filter(usuario=request.user).delete()
        else:
            Receta_Guardada.objects.create(receta=receta, usuario=request.user)
        return HttpResponse('success')
    else:
        return HttpResponse('unsuccesful')

def valorar(request):
    
    if request.method == 'GET':
        print(request.GET)
        receta_id = request.GET['receta_id']
        receta = get_object_or_404(Receta, pk=receta_id)
        valoracion = request.GET['valoracion']

        #No tiene ya valoracion
        if not Valoracion.objects.filter(receta=receta).filter(usuario=request.user).exists():
            Valoracion.objects.create(valoracion=valoracion, receta=receta, usuario=request.user)
            receta.valoracion_media = Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
            return HttpResponse(receta.valoracion_media)
        else:
            return HttpResponse('existe')
    
def valorar_seguro(request):

    if request.method == 'GET':
        receta_id = request.GET['receta_id']
        receta = get_object_or_404(Receta, pk=receta_id)
        puntos = request.GET['valoracion']
        
        valoracion = Valoracion.objects.filter(receta=receta).filter(usuario=request.user).first()
        valoracion.valoracion = puntos
        valoracion.save()
        receta.valoracion_media = Valoracion.objects.filter(receta=receta).aggregate(Avg('valoracion'))['valoracion__avg']
        
        return HttpResponse(receta.valoracion_media)
    
    return HttpResponse("unsuccessful")

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
        receta.delete()
        return redirect('perfil', username=request.user.username)




#Busqueda avanzada de recetas 
@login_required
def busqueda_avanzada(request):
    
    form = formset_factory(form=BusquedaAvanzadaForm, extra=1)
    print(form)
    formset = form()

    if request.method == 'POST':
        formset = form(request.POST)
        ingredientes = []

        if formset.is_valid():
            
            for form in formset:   #Por cada input
                try:
                    ingrediente = Ingrediente.objects.get(nombre=form.cleaned_data['ingrediente']) #Obtiene el objeto ingrediente a través del nombre
                    if not ingrediente in ingredientes: #Comprueba que no esté en la lista para que no haya repetidos
                        ingredientes.append(ingrediente)
                except Ingrediente.DoesNotExist:    #Excepción en caso de que no exista un ingrediente con el nombre introducido
                    pass
            
            #Obtiene la lista de recetas filtrando por ingrediente y sin obtener resultados
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

            mensaje = "Resultado de "
            
            for ingrediente in ingredientes:
                mensaje += ingrediente.nombre + ", "
            
            mensaje = mensaje[:-2]  #Borra los 2 último caracteres del string
            
            return render(request, 'resultado_busqueda.html', {'recetas': recetas, 'mensaje_titulo': mensaje})

    context = {
        'formset': formset
    }

    return render(request, 'busqueda_avanzada.html', context)


@login_required
def resultado_busqueda(request):
    query = request.GET.get('name')

    try:
        categoria = Categoria.objects.get(nombre=query.capitalize())
        recetas = Receta.objects.filter(categoria=categoria)
    except ObjectDoesNotExist:
        recetas = Receta.objects.filter(Q(titulo__icontains=query))
    
    
    if len(recetas) > 0:
        mensaje = "Resultados de " + query
    else:
        mensaje = 'No se ha encontrado ninguna receta con "' + query + '"'

    context = {
        'recetas': recetas,
        'mensaje_vacio': mensaje
    }
    return render(request, 'resultado_busqueda.html', context)



def error_404(request, excepction):
    return render(request, 'error_404.html')



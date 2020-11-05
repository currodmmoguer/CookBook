from django.contrib import admin
from django.contrib.auth.models import Group, User
#from .models import Perfil, Receta, Categoria, Ingrediente, Unidad_medida, Sugerencia
from .models import *
from django.db.models import Count

# Librarias para trabajar con json
from django.core.serializers.json import DjangoJSONEncoder
import json


@admin.register(Categoria)
class CategoriaReport(admin.ModelAdmin):
    list_display = ('nombre',)  # El dato del objeto que se ve en la lista
    ordering = ('nombre',)  #Orden de la lista, ordenado alfabéticamente
    categorias = Receta.objects.values('categoria').annotate(total=Count('id')) #Obtiene una lista con el id de la categoría y su cantidad de recetas
    
    for categoria in categorias: #Añade a cada item de la lista el nombre de la categoría
        categoria['categoria'] = Categoria.objects.get(pk=categoria['categoria']).nombre
    
    def changelist_view(self, request, extra_context=None): # Envía los datos a la template
        as_json = json.dumps(list(self.categorias), cls=DjangoJSONEncoder)   # Convierte la lista en un json
        extra_context = {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Perfil)
class Perfil(admin.ModelAdmin):
    exclude = ('seguidores',)   # Elimina el campo seguidores del administrador

    # Obtiene los 10 perfiles con más recetas creadas con su cantidad de recetas
    perfiles = User.objects.filter(perfil__isnull=False).annotate(num_recetas=Count('recetas')).filter(num_recetas__gt=0).order_by('-num_recetas')[:5]
    lista = []
    
    for perfil in perfiles: # Añade los perfiles con la cantidad de recetas a lista de diccionarios
        dict = {}
        dict['username'] = perfil.username
        dict['total_recetas'] = perfil.num_recetas
        lista.append(dict)
    
    def changelist_view(self, request, extra_context=None): # Envía los datos al template
        as_json = json.dumps(list(self.lista), cls=DjangoJSONEncoder)   # Convierte la lista en un json
        extra_context = {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Sugerencia)
class Sugerencia(admin.ModelAdmin):
    list_display = ('sugerencia', 'tipo', 'cantidad',)  # Indica los datos que se muestran en la lista
    list_filter = ('tipo', )    # Permite filtrar por dicho campo la lista
    ordering = ('-cantidad',)   # Ordena las sugerencias por el campo cantidad de forma descendiente
    


admin.site.site_header = "Administración de CookBook"
admin.site.site_title = "CookBook"

# Muestra por defecto
admin.site.register(Ingrediente)
admin.site.register(Unidad_medida)


admin.site.unregister(Group)    # Elimina del administración la opción de grupos (porque no se utiliza)

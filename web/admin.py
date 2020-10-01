from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import *
from django.db.models import Count

# Librarias para trabajar con json
from django.core.serializers.json import DjangoJSONEncoder
import json
 
    
@admin.register(Categoria)
class CategoriaReport(admin.ModelAdmin):
    list_display = ('nombre',)  # El dato del objeto que se ve en la lista
    ordering = ('nombre',)  #Orden de la lista, ordenado alfabéticamente
    lista = Receta.objects.values('categoria').annotate(total=Count('id')) #Obtiene una lista con el id de la categoría y su cantidad de recetas
    
    for i in lista: #Añade a cada item de la lista el nombre de la categoría
        categoria = Categoria.objects.get(pk=i['categoria'])
        i['categoria'] = categoria.nombre

    def changelist_view(self, request, extra_context=None):
        as_json = json.dumps(list(self.lista), cls=DjangoJSONEncoder)   # Convierte la lista en un json
        extra_context = extra_context or {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Perfil)
class Perfil(admin.ModelAdmin):
    #exclude = ('seguidores',)   # Elimina el campo seguidores del administrador

    # Obtiene los 10 perfiles con más recetas creadas
    perfiles = User.objects.filter(perfil__isnull=False).annotate(num_recetas=Count('recetas')).filter(num_recetas__gt=0).order_by('-num_recetas')[:5]
    lista = []
    
    for perfil in perfiles:
        dict = {}
        dict['username'] = perfil.username
        dict['total_recetas'] = perfil.num_recetas
        lista.append(dict)
        
    
    def changelist_view(self, request, extra_context=None):
        as_json = json.dumps(list(self.lista), cls=DjangoJSONEncoder)   # Convierte la lista en un json
        extra_context = extra_context or {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

        

@admin.register(Sugerencia)
class Sugerencia(admin.ModelAdmin):
    list_display = ('sugerencia', 'tipo', 'cantidad',)  # Indica los datos que se muestran en la lista
    list_filter = ('tipo', )    # Permite filtrar por dicho campo la lista
    ordering = ('-cantidad',)

@admin.register(Notificacion)
class Notificacion(admin.ModelAdmin):
    list_display = ('usuario_origen', 'usuario_destino', 'tipo', 'visto', )

admin.site.register(Ingrediente)
admin.site.register(Unidad_medida)


admin.site.unregister(Group)    # Elimina del administración la opción de grupos (porque no se utiliza)
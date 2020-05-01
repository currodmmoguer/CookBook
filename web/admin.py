from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *


from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
import json

@admin.register(Categoria)
class CategoriaReport(admin.ModelAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    lista = Receta.objects.values('categoria').annotate(total=Count('id'))
    
    for i in lista:
        categoria = Categoria.objects.get(pk=i['categoria'])
        i['categoria'] = categoria.nombre

    print(lista)
    
    def changelist_view(self, request, extra_context=None):
        chart_data = (self.lista)
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Perfil)
class Perfil(admin.ModelAdmin):
    exclude = ('seguidores',)

@admin.register(Sugerencia)
class Sugerencia(admin.ModelAdmin):
    list_display = ('sugerencia', 'tipo',)
    list_filter = ('tipo', )

admin.site.register(Ingrediente)
admin.site.register(Unidad_medida)
admin.site.unregister(Group)
admin.site.register(Receta_Guardada)


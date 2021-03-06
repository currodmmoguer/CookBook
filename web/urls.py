from django.urls import path
from . import views

urlpatterns = [
    path('hay_notificaciones/', views.hay_notificaciones, name="hay_notificaciones"),   #Ajax-Comprueba que el usuario tenga notificaciones
    path('sugerencia/', views.sugerencia, name="sugerencia"),   #Ajax-Envía sugerencia al administrador
    path('valorar/', views.valorar, name="valorar"),    #Sirve para cuando se da al botón valorar
    path('valorar-seg/', views.valorar_seguro, name="valorar_seguro"),  #Sirve cuando se valora desde el modal
    path('buscar/', views.busqueda_avanzada, name='busqueda_avanzada'),     #Buscqueda avanzada de receta
    path('busqueda/', views.resultado_busqueda, name="busqueda"),   #Buscar requeta navbar
    path('categoria/<c>/', views.resultado_busqueda_categoria, name="busqueda_categoria"),   # Mostrar las recetas de una categorías
    path('guardar/', views.guardar, name="guardar"),    #Guardar receta
    path('', views.index, name="index"),    #Página princial
    path('<username>/', views.perfil, name="perfil"),   #Perfil
    path('receta/<int:pk>/', views.receta, name="receta"),  #Vista receta
    path('receta/nueva/', views.nueva_receta, name="nueva_receta"),  #Crear receta
    path('receta/<int:pk>/edit/', views.editar_receta, name="editar_receta"),   #Editar receta
    path('<username>/pass-edit/', views.editar_pass, name="editar_pass"),   #Editar contraseña
    path('rrss-edit', views.editar_rrss, name="editar_rrss"),   #Editar las RRSS
    path('notificaciones', views.notificaciones, name="notificaciones"),    #Muestra las notificaciones
    path('signup', views.registro, name="registro"),    #Vista registro
    path('<username>/guardadas/', views.recetas_guardadas, name='recetas_guardadas'),   #Vista recetas guardadas
    path('<username>/seguidores', views.seguidores, name="seguidores"), #Vista lista de seguidores
    path('<username>/siguiendo', views.siguiendo, name="siguiendo"),    #Vista lista de siguiendo
    path('<username>/perfil-edit/', views.editar_perfil, name="editar_perfil"), #Vista editar perfil
    path('<pk>/seguir', views.seguir_dejar, name="seguir"),   #Seguir/Dejar a usuario
    #path('<pk>/dejar-seguir', views.dejar_seguir, name="dejar_seguir"),     #Dejar de seguir a usuario
    path('eliminar', views.eliminar_cuenta, name="eliminar_cuenta"),    #Eliminar cuenta
    path('eliminar-foto', views.eliminar_foto, name="eliminar_foto"),   #Eliminar foto de perfil
    path('eliminar-receta/<pk>/', views.eliminar_receta, name="eliminar_receta"),   #Eliminar receta
    path('receta/<pk>/publicar', views.publicar, name="publicar"),  #Publicar o no una receta
]
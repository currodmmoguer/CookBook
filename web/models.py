from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Sum
from datetime import datetime
import os


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'categoria'

    def __str__(self):
        return self.nombre


class Unidad_medida(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'unidad_medida'
        verbose_name = 'Unidad de medida'
        verbose_name_plural = 'Unidades de medida'

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    imagen_terminada = models.ImageField(upload_to='receta', db_column='imagen')
    raciones = models.CharField(max_length=5, null=True, blank=True)
    tiempo_estimado = models.CharField(max_length=50, null=True, blank=True)
    publico = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_DEFAULT, default=1)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recetas")
    usuarios_guardado = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="recetas_guardadas", blank=True)
    valoracion_media = ""

    class Meta:
        db_table = 'receta'

    def __str__(self):
        return self.titulo

    def guardar(self, user):    #Guarda o quita de la lista al usuario indicado

    	if not user in self.usuarios_guardado.all():
    		self.usuarios_guardado.add(user)
    	else:
    		self.usuarios_guardado.remove(user)

    def publicar(self): #Pone público/privado la receta, devuelve el valor de publico
        self.publico = not self.publico
        self.save()
        return self.publico



class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name="perfil")
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    imagen_perfil = models.ImageField(upload_to='perfil', default="perfil/avatar-no-img.webp", null=True, blank=True, db_column="imagen")
    seguidores = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='seguidor')
    

    class Meta:
        db_table = 'perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
    	return self.usuario.username

    def total_seguidores(self): #Obtiene el número total de seguidores
    	if not self.seguidores.all():
    		return 0
    	else:
    		return self.seguidores.all().count()


    def set_imagen(self, imagen):   #Añade una imagen de perfil
    	if imagen is None: #Si no hay ninguna le pone la de por defecto
    		self.imagen_perfil.name = "perfil/avatar-no-img.webp"
    	else:
    		self.imagen_perfil = imagen
    	self.save()


    def add_seguidor(self, perfil):
        if perfil not in self.seguidores.all():
            self.seguidores.add(perfil)
            self.save()

    def dejar_seguir(self, perfil):
        if perfil in self.seguidores.all():
            self.seguidores.remove(perfil)
            self.save()

"""
    def es_seguidor(self, perfil):
    	cursos = connection.cursor()
    	sentencia = "select * from web_perfil_seguidores where to_perfil_id= " + str(perfil.pk) + " and from_perfil_id=" + str(self.usuario.pk)
    	row = cursor.execute(sentencia)

    	if row == 0:
    		return False
    	else:
    		return True"""




class Comentario(models.Model):
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comentario_respuesta = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='respuestas')

    class Meta:
        db_table = 'comentario'

    def __str__(self):
        return self.texto

    def fecha_format(self):
    	return self.fecha.strftime('%d-%m-%Y %H:%M')


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'ingrediente'

    def __str__(self):
    	return self.nombre

class Ingrediente_Receta(models.Model):
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name="ingredientes")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.DO_NOTHING)
    cantidad = models.CharField(max_length=30)
    unidad_medida = models.ForeignKey(
        Unidad_medida, on_delete=models.SET("Otros"))

    class Meta:
        db_table = 'receta_ingrediente'

    """def __str__(self):
        return "{} - {} + {}".format(self.pk, self.ingrediente, self.receta)"""


class Paso(models.Model):
    texto = models.TextField()
    imagen_paso = models.ImageField(upload_to='paso', null=True, blank=True)
    posicion = models.IntegerField()
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name="pasos")

    class Meta:
        db_table = 'paso'

    def __str__(self):
    	return self.texto + ", imagen: " + str(self.imagen_paso)


class Valoracion(models.Model):
    valoracion = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)])
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="valoraciones")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'valoracion'
        verbose_name_plural = 'Valoraciones'

    def __str__(self):
        return self.valoracion

class Sugerencia(models.Model):
    choices = (
        ('cat', 'Categoria'),
        ('udm', 'Unidad de medida'),
        )

    tipo = models.CharField(max_length=3, choices=choices)
    sugerencia = models.CharField(max_length=255)

    def __str__(self):
        return self.sugerencia


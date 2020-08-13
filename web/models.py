from django.db import models
from django.utils import timezone
from django.conf import settings

from django.db.models import Avg

# Sirve para controlar el máximo y mínimo de la valoración
from django.core.validators import MaxValueValidator, MinValueValidator


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
    valoracion_media = ""

    class Meta:
        db_table = 'receta'

    def __str__(self):
        return self.titulo

    def publicar(self): #Pone público/privado la receta, devuelve el valor de publico
        self.publico = not self.publico
        self.save()
        return self.publico



class Perfil(models.Model):
    _IMG_DEFAULT = "perfil/avatar-no-img.webp"
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name="perfil")
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    imagen_perfil = models.ImageField(upload_to='perfil', default=_IMG_DEFAULT, null=True, blank=True, db_column="imagen")
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
    		self.imagen_perfil.name = self._IMG_DEFAULT
    	else:
    		self.imagen_perfil = imagen
    	self.save()


    def add_seguidor(self, perfil): # Añade un usuario a la lista de seguidores
        if perfil not in self.seguidores.all():
            self.seguidores.add(perfil)
            self.save()

    def dejar_seguir(self, perfil): # Elimina el usuario de la lista de seguidores
        if perfil in self.seguidores.all():
            self.seguidores.remove(perfil)
            self.save()


class Receta_Guardada(models.Model):
    receta = receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="guardadas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recetas_guardadas")
    fecha = models.DateTimeField(default=timezone.now)

    class Meta():
        db_table = "recetas_guardadas"

    def save(self, *args, **kwargs):
        if Receta_Guardada.objects.filter(receta=self.receta).filter(usuario=self.usuario).exists():
            return False
        else:
            super(Receta_Guardada, self).save(*args, **kwargs)

    def __str__(self):
        return self.receta.titulo + " - " + self.usuario.username

class Comentario(models.Model):
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comentario_respuesta = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='respuestas')

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

class Ingrediente_Receta(models.Model): # Relacion entre ingrediente y receta
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="ingredientes")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.DO_NOTHING)
    cantidad = models.FloatField(max_length=30)
    unidad_medida = models.ForeignKey(Unidad_medida, on_delete=models.SET("Otros"), default=1)

    class Meta:
        db_table = 'receta_ingrediente'


class Paso(models.Model):
    texto = models.TextField()
    imagen_paso = models.ImageField(upload_to='paso', null=True, blank=True)
    posicion = models.PositiveIntegerField()
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="pasos")

    class Meta:
        db_table = 'paso'

    def __str__(self):
    	return self.texto + ", imagen: " + str(self.imagen_paso)


class Valoracion(models.Model):
    valoracion = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="valoraciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'valoracion'
        verbose_name_plural = 'Valoraciones'

    def __str__(self):
        return str(self.valoracion) + str(self.receta) + str(self.usuario)

class Sugerencia(models.Model):
    choices = (
        ('cat', 'Categoria'),
        ('udm', 'Unidad de medida'),
    )

    tipo = models.CharField(max_length=3, choices=choices, default=choices[0])
    sugerencia = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'sugerencia'

class Notificacion(models.Model):
    choices = (
        ('comentario', 'Comentario'),
        ('respuesta', 'Respuesta'),
        ('valoracion', 'Valoracion'),
        ('siguiendo', 'Siguiendo'),
    )
    usuario_destino = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificaciones")
    usuario_origen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    visto = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, choices=choices, default=choices[0])
    caso = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        #db_table = 'notificacion'
        verbose_name_plural = 'Notificaciones'
    def __str__(self):
        return "Usuario origen: {}, Usuario destino: {}, Tipo: {}".format(self.usuario_destino, self.usuario_origen, self.tipo)

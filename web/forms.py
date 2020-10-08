from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from os import remove
# Recortar image
from PIL import Image


class RegistroUserForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña*")
    
    class Meta:
        model = User
        fields = ('username', 'email','first_name', 'last_name', 'password', )
        labels = {
            'username': 'Usuario*',
            'email': 'Email*',
            'first_name': 'Nombre*',
            'last_name': 'Apellido',
            'password': 'Contraseña*'
        }
        widgets = {
            'email': forms.TextInput(attrs={'required': "required"}),
            'first_name': forms.TextInput(attrs={'required': "required"}),
            'password': forms.PasswordInput()
        
        }

    def save(self, commit=False):
        user = super(RegistroUserForm, self).save(commit=False)
        print(self.cleaned_data)
        cd = self.cleaned_data
        user.set_password(cd['password'])
        user.first_name = cd['first_name']
        user.last_name = cd['last_name']
        user.email = cd['email']
        user.save()
        return user

    

class RegistroPerfilForm(forms.ModelForm):
   
    class Meta:
        model = Perfil
        fields = ('descripcion', 'imagen_perfil',)
        labels = {
            'descripcion': 'Sobre tí...',
            'imagen_perfil': 'Subir foto de perfil'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4})
        }

        def save(self, usuario):
            print("entra")
            print(self.cleaned_data)
            cd = self.cleaned_data
            perfil = Perfil(usuario=usuario)
            perfil.descripcion = cd['descripcion']
            perfil.set_imagen(cd['imagen_perfil'])
            perfil.save()

class EditarPerfilForm(forms.Form):
    imagen_perfil = forms.ImageField(required=False, label="Elegir imagen...")
    nombre = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': "form-control"}))
    apellido = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    descripcion = forms.CharField(max_length=255, label="Descripción", required=False, widget=forms.Textarea(attrs={'rows':3, 'class': "form-control"}))
    email = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': "form-control"}))
    val_img = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self, usuario):
        cd = self.cleaned_data
        usuario.first_name = cd['nombre']
        usuario.last_name = cd['apellido']
        usuario.perfil.descripcion = cd['descripcion']
        usuario.email = cd['email']

        if not cd['imagen_perfil'] is None:
            valores = list(map(float, cd['val_img'].split(";")))
            if not usuario.perfil.imagen_perfil.name == "perfil/avatar-no-img.webp":   # Cromprueba que no sea la imagen por defecto
                remove(usuario.perfil.imagen_perfil.path) # Borra la imagen anterior
            usuario.perfil.set_imagen(cd['imagen_perfil'])
        usuario.save()
        usuario.perfil.save()

        # Guarda la imagen recortada
        # Se hace ahora porque tiene que está guardada la imagen ya
        if not cd['imagen_perfil'] is None:
            image = Image.open(usuario.perfil.imagen_perfil)
            cropped_image = image.crop((valores[0], valores[1], valores[0] + valores[2], valores[1] + valores[3]))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            resized_image.save(usuario.perfil.imagen_perfil.path)  # Lo guarda con el mismo nombre del aterior (lo remplaza)



class PasswordChangeForm(PasswordChangeForm):
    
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'

class EditarRRSSForm(forms.Form):
    facebook = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    instagram = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    twitter = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    youtube = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))

    def save(self, perfil):
        cd = self.cleaned_data
        # De cada campo comprueba que no se haya cambiado
        if perfil.facebook != cd['facebook']:
            perfil.facebook = cd['facebook']
            
        if perfil.instagram != cd['instagram']:
            perfil.instagram = cd['instagram']
            
        if perfil.twitter != cd['twitter']:
            perfil.twitter = cd['twitter']

        if perfil.youtube != cd['youtube']:
            perfil.youtube = cd['youtube']
            
        perfil.save()
    

class RecetaForm(forms.ModelForm):
    imagen_terminada = forms.ImageField(label="Subir foto del plato")
    
    class Meta:
        model = Receta
        fields = ('titulo', 'imagen_terminada', 'raciones', 'tiempo_estimado', 'categoria')
        labels = {
            'titulo': 'Título*',
            'raciones': 'Comensales',
            'tiempo_estimado': 'Tiempo de elaboración'
        }
        widgets = {
            'raciones': forms.NumberInput(attrs={'placeholder': 'Ej: 2'}),
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Ej: 30 minutos'}),
            'categoria': forms.Select(attrs={'class': 'custom-select wrap-input2 validate-input', 'required': 'required'}),
        }

    
class IngredienteFormset(forms.ModelForm):
    ingrediente = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'required': "required"}))
    
    class Meta:
        model = Ingrediente_Receta
        fields = ('cantidad', 'unidad_medida')
        widgets = { #Añade clases al elemento en el archivo html
            'unidad_medida': forms.Select(attrs={'class': 'custom-select wrap-input2 validate-input', 'required': 'required'}),
            'cantidad': forms.TextInput(attrs={'required': "required"})
        }
    
class IngredienteEditFormset(forms.ModelForm):
    ingrediente = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'required': "required"}))
    
    class Meta:
        model = Ingrediente_Receta
        fields = ('cantidad', 'unidad_medida')
        widgets = { #Añade clases al elemento en el archivo html
            'unidad_medida': forms.Select(attrs={'class': 'custom-select wrap-input2 validate-input'}),
            'cantidad': forms.TextInput(attrs={'required': "required"})
        }

        
class PasoFormset(forms.ModelForm):
    
    class Meta:
        model = Paso
        fields = ('texto', 'imagen_paso',)
        labels = {
            'texto': 'Descripción...',
            'imagen_paso': 'Subir imagen'
        }
        widgets = {
            'texto': forms.Textarea(attrs={'rows':3, 'required': 'required'}),
        }



class ComentarioForm(forms.ModelForm):

    class Meta:
        model = Comentario
        fields = ('texto',)
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'placeholder': 'Escribe un comentario...', 'required': 'required'}),
        }

    def save(self, usuario, receta):
        print(self.__dict__)
        comentario = self.instance
        comentario.usuario = usuario
        comentario.receta = receta  # Le añade la receta
        comentario.save()
        return comentario


class RespuestaForm(forms.ModelForm):

    class Meta:
        model = Comentario
        fields = ('texto',)

    def save(self, receta, usuario):
        texto = self.cleaned_data['texto']
        padre =Comentario.objects.get(pk=self.data.get('comentario-respuesta'))
        comentario = Comentario.objects.create(
                texto=texto, receta=receta, usuario=usuario, comentario_respuesta=padre)
        return comentario

class ValoracionForm(forms.Form):
    valoracion = forms.CharField(max_length=1)

    def save(self, usuario, receta, valoracion):
        return Valoracion.objects.create(valoracion=valoracion, receta=receta, usuario=usuario)
    

class BusquedaAvanzadaForm(forms.Form):
    ingrediente = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'required': '', 'placeholder': 'Introduce el ingrediente'}))


class SugForm(forms.ModelForm):
    info = "Si hay una categoria o unidad de medida que falte, por favor, comuníquenoslo."
    
    class Meta:
        model = Sugerencia
        fields = ('tipo', 'sugerencia',)
        labels = {
            'sugerencia': 'Escribe tu sugerencia'
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'custom-select wrap-input2 validate-input'}),
        }
    
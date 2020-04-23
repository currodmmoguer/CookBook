from django import forms
from .models import *
from django.contrib.auth.models import User

class RegistroUserForm(forms.ModelForm):
    password2 = forms.PasswordInput()
    class Meta:
        model = User
        fields = ('username', 'email','first_name', 'last_name', 'password',)

class RegistroPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ('descripcion', 'imagen_perfil',)

class EditarPerfilForm(forms.Form):
    imagen_perfil = forms.ImageField(required=False)
    nombre = forms.CharField(max_length=30)
    apellido = forms.CharField(max_length=50, required=False)
    descripcion = forms.CharField(max_length=255, required=False)

class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ('titulo', 'imagen_terminada', 'raciones', 'tiempo_estimado', 'categoria')

class IngredienteFormset(forms.ModelForm):
    ingrediente = forms.CharField(max_length=100)
    class Meta:
        model = Ingrediente_Receta
        fields = ('cantidad', 'unidad_medida')

class PasoFormset(forms.ModelForm):
    class Meta:
        model = Paso
        fields = ('texto', 'imagen_paso',)
        widgets = {
            'texto': forms.Textarea(attrs={'rows':3}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('texto',)

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('texto',)

class ValoracionForm(forms.Form):
    valoracion = forms.CharField(max_length=1)

    def save(self, usuario, receta, valoracion):
        return Valoracion.objects.create(valoracion=valoracion, receta=receta, usuario=usuario)
    

class BusquedaAvanzadaForm(forms.Form):
    ingrediente = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Introduce el ingrediente'}))

class SugForm(forms.Form):
    texto = forms.CharField(max_length=255)

from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class RegistroUserForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'email','first_name', 'last_name', 'password', )
        widgets = {
            'email': forms.TextInput(attrs={'required': "required"}),
            'first_name': forms.TextInput(attrs={'required': "required"})
        }
    

class RegistroPerfilForm(forms.ModelForm):
   
    class Meta:
        model = Perfil
        fields = ('descripcion', 'imagen_perfil',)
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4})
        }


class EditarPerfilForm(forms.Form):
    imagen_perfil = forms.ImageField(required=False)
    nombre = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': "form-control"}))
    apellido = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    descripcion = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows':3, 'class': "form-control"}))
    

class PasswordChangeForm(PasswordChangeForm):
    
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'
            
    

class RecetaForm(forms.ModelForm):
    imagen_terminada = forms.ImageField()
    
    class Meta:
        model = Receta
        fields = ('titulo', 'imagen_terminada', 'raciones', 'tiempo_estimado', 'categoria')
        widgets = {
            'raciones': forms.TextInput(attrs={'placeholder': 'Ej: 2-3'}),
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Ej: 30 minutos'})
            
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
        }

        
class PasoFormset(forms.ModelForm):
    
    class Meta:
        model = Paso
        fields = ('texto', 'imagen_paso',)
        widgets = {
            'texto': forms.Textarea(attrs={'rows':3, 'required': 'required'}),
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
    ingrediente = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'required': '', 'placeholder': 'Introduce el ingrediente'}))


class SugForm(forms.ModelForm):
    
    class Meta:
        model = Sugerencia
        fields = ('tipo', 'sugerencia',)
        widgets = {
            'tipo': forms.Select(attrs={'class': 'custom-select wrap-input2 validate-input'}),
        }
    
    #Hace que se elimine la opción por defecto de -------
    def __init__(self, *args, **kwargs):
        super(SugForm, self).__init__(*args, **kwargs)
        # Obtiene la misma lista pero quitando el primer elemento
        self.fields['tipo'].widget.choices = self.fields['tipo'].choices[1:]

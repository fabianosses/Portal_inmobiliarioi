from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['nro_region', 'nombre']
#        widgets = {
#            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#        }

class ComunaForm(forms.ModelForm):
    class Meta:
        model = Comuna
        fields = ['region', 'nombre']
#        widgets = {
#            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#            'region': forms.Select(attrs={'class': 'form-control'}),
#        }

class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = [
            'propietario', 'nombre', 'descripcion', 'm2_construidos', 
            'm2_totales', 'estacionamientos', 'habitaciones', 'banos', 
            'direccion', 'precio_mensual', 'comuna', 'tipo_inmueble'
        ]
#        widgets = {
#            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
#            'comuna': forms.Select(attrs={'class': 'form-control'}),
#            'tipo_inmueble': forms.Select(attrs={'class': 'form-control'}),
#        }


class SolicitudArriendoForm(forms.ModelForm):
    class Meta:
        model = SolicitudArriendo
        fields = ['mensaje']
#        widgets = {
#            'inmueble': forms.Select(attrs={'class': 'form-control'}),
#            'arrendatario': forms.Select(attrs={'class': 'form-control'}),
#            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
#        }

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario', 'rut', 'password']
#        widgets = {
#            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
#            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
#        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = PerfilUsuario
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'rut',
            'tipo_usuario',
            'password1',
            'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
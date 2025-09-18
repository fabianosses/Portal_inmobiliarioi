# backend/portal/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
import requests

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['nro_region', 'nombre']

class ComunaForm(forms.ModelForm):
    class Meta:
        model = Comuna
        fields = ['region', 'nombre']

class InmuebleForm(forms.ModelForm):

    # Campos para la selección de ubicación usando la API
    region_codigo = forms.ChoiceField(
        label='Región',
        required=True,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_region',
            'onchange': 'cargarComunas()'
        })
    )
    
    comuna_codigo = forms.ChoiceField(
        label='Comuna',
        required=True,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_comuna'
        })
    )

    class Meta:
        model = Inmueble
        fields = [
            'propietario', 'nombre', 'descripcion', 'm2_construidos', 
            'm2_totales', 'estacionamientos', 'habitaciones', 'banos', 
            'direccion', 'precio_mensual', 'tipo_inmueble',
            'region_codigo', 'comuna_codigo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar opciones de regiones
        self.fields['region_codigo'].choices = self.get_regiones_choices()
        self.fields['comuna_codigo'].choices = [('', 'Primero selecciona una región')]
        
        # Si ya existe la instancia, cargar los valores
        if self.instance and self.instance.region_codigo:
            self.fields['region_codigo'].initial = self.instance.region_codigo
            # Cargar comunas para la región seleccionada
            self.fields['comuna_codigo'].choices = self.get_comunas_choices(self.instance.region_codigo)
            if self.instance.comuna_codigo:
                self.fields['comuna_codigo'].initial = self.instance.comuna_codigo

    def get_regiones_choices(self):
        """Obtener choices de regiones desde la API"""
        try:
            response = requests.get('https://apis.digital.gob.cl/dpa/regiones', timeout=5)
            regiones = response.json()
            choices = [(r['codigo'], r['nombre']) for r in regiones]
            return [('', 'Selecciona una región')] + choices
        except:
            return [('', 'Error cargando regiones')]
    
    def get_comunas_choices(self, region_code):
        """Obtener choices de comunas para una región"""
        try:
            response = requests.get(f'https://apis.digital.gob.cl/dpa/regiones/{region_code}/comunas', timeout=5)
            comunas = response.json()
            choices = [(c['codigo'], c['nombre']) for c in comunas]
            return [('', 'Selecciona una comuna')] + choices
        except:
            return [('', 'Error cargando comunas')]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Guardar los nombres de región y comuna
        region_codigo = self.cleaned_data.get('region_codigo')
        comuna_codigo = self.cleaned_data.get('comuna_codigo')
        
        if region_codigo:
            try:
                response = requests.get(f'https://apis.digital.gob.cl/dpa/regiones/{region_codigo}', timeout=5)
                if response.status_code == 200:
                    instance.region_nombre = response.json().get('nombre', '')
            except:
                instance.region_nombre = ''
        
        if comuna_codigo:
            try:
                response = requests.get(f'https://apis.digital.gob.cl/dpa/comunas/{comuna_codigo}', timeout=5)
                if response.status_code == 200:
                    instance.comuna_nombre = response.json().get('nombre', '')
            except:
                instance.comuna_nombre = ''
        
        if commit:
            instance.save()
        
        return instance

class SolicitudArriendoForm(forms.ModelForm):
    class Meta:
        model = SolicitudArriendo
        fields = ['mensaje']

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario', 'rut', 'password']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

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
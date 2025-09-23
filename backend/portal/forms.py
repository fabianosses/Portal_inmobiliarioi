# backend/portal/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Inmueble, SolicitudArriendo, PerfilUsuario, Region, Comuna
from .services import ChileanLocationService
import requests, logging

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['nro_region', 'nombre']

class ComunaForm(forms.ModelForm):
    class Meta:
        model = Comuna
        fields = ['region', 'nombre']

logger = logging.getLogger(__name__)

class InmuebleForm(forms.ModelForm):
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
            'id': 'id_comuna',
            'disabled': 'disabled'
        })
    )

    class Meta:
        model = Inmueble
        fields = [
            'nombre', 'imagen', 'descripcion', 'm2_construidos', 
            'm2_totales', 'estacionamientos', 'habitaciones', 'banos', 
            'direccion', 'precio_mensual', 'tipo_inmueble',
            'region_codigo', 'comuna_codigo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'm2_construidos': forms.NumberInput(attrs={'class': 'form-control'}),
            'm2_totales': forms.NumberInput(attrs={'class': 'form-control'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'estacionamientos': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_inmueble': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar regiones
        self.cargar_regiones()
        
        # Cargar comunas si estamos editando
        if self.instance and self.instance.pk and self.instance.region_codigo:
            self.cargar_comunas_para_edicion()

    def cargar_regiones(self):
        """Carga las regiones en el campo correspondiente"""
        try:
            regiones = ChileanLocationService.get_regiones()
            if regiones:
                choices = [(r['codigo'], r['nombre']) for r in regiones]
                self.fields['region_codigo'].choices = [('', 'Selecciona una región')] + choices
            else:
                self.fields['region_codigo'].choices = [('', 'No se pudieron cargar las regiones')]
                logger.error("No se pudieron obtener las regiones")
        except Exception as e:
            self.fields['region_codigo'].choices = [('', 'Error cargando regiones')]
            logger.error(f"Error cargando regiones: {e}")

    def cargar_comunas_para_edicion(self):
        """Carga las comunas cuando se está editando un inmueble"""
        try:
            comunas = ChileanLocationService.get_comunas_by_region(self.instance.region_codigo)
            if comunas:
                comuna_choices = [(c['codigo'], c['nombre']) for c in comunas]
                self.fields['comuna_codigo'].choices = [('', 'Selecciona una comuna')] + comuna_choices
                
                # Si hay una comuna seleccionada, habilitar el campo
                if self.instance.comuna_codigo:
                    self.fields['comuna_codigo'].widget.attrs.pop('disabled', None)
            else:
                self.fields['comuna_codigo'].choices = [('', 'No hay comunas para esta región')]
        except Exception as e:
            self.fields['comuna_codigo'].choices = [('', 'Error cargando comunas')]
            logger.error(f"Error cargando comunas para edición: {e}")

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
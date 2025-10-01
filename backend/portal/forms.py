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
            'id': 'id_region_codigo'
        })
    )
    
    comuna_codigo = forms.ChoiceField(
        label='Comuna',
        required=True,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_comuna_codigo',
            'disabled': True
        })
    )

    class Meta:
        model = Inmueble
        fields = [
            'nombre', 'imagen', 'descripcion', 'm2_construidos', 
            'm2_totales', 'estacionamientos', 'habitaciones', 'banos', 
            'direccion', 'precio_mensual', 'tipo_inmueble',  # precio_mensual DEBE estar aquí
            'region_codigo', 'comuna_codigo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Casa moderna en sector tranquilo'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Principal #123'}),
            'precio_mensual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1', 
                'step': '1000',
                'placeholder': 'Ej: 350000'
            }),
            'm2_construidos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'm2_totales': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'estacionamientos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tipo_inmueble': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        help_texts = {
            'precio_mensual': 'Precio mensual en pesos chilenos',
            'm2_construidos': 'Metros cuadrados construidos',
            'm2_totales': 'Metros cuadrados totales del terreno',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cargar_regiones()
        self._cargar_comunas_si_existe()

    def _cargar_regiones(self):
        """Carga las regiones de forma segura"""
        try:
            regiones = ChileanLocationService.get_regiones()
            choices = [('', 'Selecciona una región')] + [(r['codigo'], r['nombre']) for r in regiones]
            self.fields['region_codigo'].choices = choices
        except Exception as e:
            logger.error(f"Error cargando regiones: {e}")
            self.fields['region_codigo'].choices = [('', 'Error cargando regiones')]

    def _cargar_comunas_si_existe(self):
        """Carga comunas si el inmueble ya existe"""
        if self.instance and self.instance.pk and self.instance.region_codigo:
            try:
                comunas = ChileanLocationService.get_comunas_by_region(self.instance.region_codigo)
                comuna_choices = [('', 'Selecciona una comuna')] + [(c['codigo'], c['nombre']) for c in comunas]
                self.fields['comuna_codigo'].choices = comuna_choices
                self.fields['comuna_codigo'].widget.attrs.pop('disabled', None)
            except Exception as e:
                logger.error(f"Error cargando comunas para edición: {e}")

    def clean(self):
        """Validaciones cruzadas"""
        cleaned_data = super().clean()
        
        m2_construidos = cleaned_data.get('m2_construidos')
        m2_totales = cleaned_data.get('m2_totales')
        
        if m2_construidos and m2_totales and m2_construidos > m2_totales:
            raise forms.ValidationError({
                'm2_construidos': 'Los m² construidos no pueden ser mayores a los m² totales'
            })
        
        return cleaned_data

    def clean_precio_mensual(self):
        precio = self.cleaned_data.get('precio_mensual')
        if precio and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0")
        return precio
    
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        
        # Si no hay imagen o es un string (cuando no se cambia la imagen existente)
        if not imagen or isinstance(imagen, str):
            return imagen
        
        # Solo validar si es un archivo nuevo
        if hasattr(imagen, 'size'):
            # Validar tamaño máximo (5MB)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede ser mayor a 5MB")
            
            # Validar tipo de archivo
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            if not imagen.name.lower().endswith(valid_extensions):
                raise forms.ValidationError("Solo se permiten imágenes JPG, PNG o WebP")
        
        return imagen
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        self._guardar_nombres_ubicacion(instance)
        
        if commit:
            instance.save()
        
        return instance
    
    def _guardar_nombres_ubicacion(self, instance):
        """Guarda los nombres de región y comuna"""
        region_codigo = self.cleaned_data.get('region_codigo')
        comuna_codigo = self.cleaned_data.get('comuna_codigo')
        
        if region_codigo:
            try:
                regiones = ChileanLocationService.get_regiones()
                region_nombre = next((r['nombre'] for r in regiones if r['codigo'] == region_codigo), '')
                instance.region_nombre = region_nombre
            except Exception as e:
                logger.error(f"Error guardando nombre de región: {e}")
        
        if comuna_codigo and region_codigo:
            try:
                comunas = ChileanLocationService.get_comunas_by_region(region_codigo)
                comuna_nombre = next((c['nombre'] for c in comunas if c['codigo'] == comuna_codigo), '')
                instance.comuna_nombre = comuna_nombre
            except Exception as e:
                logger.error(f"Error guardando nombre de comuna: {e}")
    

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
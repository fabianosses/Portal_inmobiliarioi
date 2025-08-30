from django import forms
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
        fields = ['inmueble', 'arrendatario', 'mensaje', 'estado']
#        widgets = {
#            'inmueble': forms.Select(attrs={'class': 'form-control'}),
#            'arrendatario': forms.Select(attrs={'class': 'form-control'}),
#            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
#        }
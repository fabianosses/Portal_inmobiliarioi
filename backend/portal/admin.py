# backend/portal/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import *

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass

@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    pass

@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'precio_mensual', 'tipo_inmueble', 'comuna_nombre')
    search_fields = ('nombre', 'direccion', 'comuna_nombre')
    list_filter = ('tipo_inmueble', 'region_nombre') # Filtros
    readonly_fields = ('creado', 'actualizado')  # Campos

    def save_model(self, request, obj, form, change):
        if change:
            obj.ultima_modificacion = timezone.now()
        else:
            obj.fecha_creacion = timezone.now()
        obj.save()


@admin.register(SolicitudArriendo)
class SolicitudArriendoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'inmueble', 'arrendatario', 'estado', 'creado')
    list_filter = ('estado', 'creado')
    readonly_fields = ('uuid', 'creado', 'actualizado')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'rut')
    list_filter = ('tipo_usuario',)
    fieldsets = UserAdmin.fieldsets + (
        ('Información extra', {'fields': ('tipo_usuario', 'rut', 'imagen')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo_usuario', 'rut')}),
    )
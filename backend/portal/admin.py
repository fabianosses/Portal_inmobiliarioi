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
    list_display = ['nombre', 'propietario', 'esta_publicado', 'creado']
    list_filter = ['esta_publicado', 'tipo_inmueble', 'region_nombre']
    actions = ['aprobar_inmuebles']
    
    def aprobar_inmuebles(self, request, queryset):
        queryset.update(esta_publicado=True)
        self.message_user(request, f"{queryset.count()} inmuebles aprobados")


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
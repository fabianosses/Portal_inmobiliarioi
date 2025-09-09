from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
    pass

@admin.register(SolicitudArriendo)
class SolicitudArriendoAdmin(admin.ModelAdmin):
    pass

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información extra', {'fields': ('tipo_usuario', 'rut', 'imagen')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('None', {'fields': ('tipo_usuario', 'rut')}),
    )
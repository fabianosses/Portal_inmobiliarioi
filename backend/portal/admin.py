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
    list_display = ('nombre', 'direccion', 'precio')
    search_fields = ('nombre', 'direccion')
    list_filter = ('precio', 'region')
    readonly_fields = ('fecha_creacion', 'ultima_modificacion') 

    def save_model(self, request, obj, form, change):
        if change:
            obj.ultima_modificacion = timezone.now()
        else:
            obj.fecha_creacion = timezone.now()
        obj.save()


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
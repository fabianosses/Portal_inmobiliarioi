# backend/portal/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
import uuid
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import transaction

# Create your models here.

class Region(models.Model):
    nro_region = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        permissions = [
            ("gestionar_region", "Puede gestionar regiones"),
        ]

    def __str__(self):
        return f"{self.nombre} ||| número de región es: {self.nro_region}"

class Comuna(models.Model):
    nombre = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="comunas")

    class Meta:
        permissions = [
            ("gestionar_comuna", "Puede gestionar comunas"),
        ]

    def __str__(self):
        return f"{self.nombre} ||| número de región es: {self.region.nombre}"

# modelo de inmueble
class Inmueble(models.Model):
    class Tipo_de_inmueble(models.TextChoices):
        casa = "CASA", _("Casa")
        depto = "DEPARTAMENTO", _("Departamento")
        parcela = "PARCELA", _("Parcela")

    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inmuebles", null=True, blank=True)
    nombre = models.CharField(max_length=100)
#    imagen = models.ImageField(upload_to='inmuebles/', default='sin_imagen/')
    descripcion = models.TextField()
    m2_construidos = models.FloatField(default=0)
    m2_totales = models.FloatField(default=0)
    estacionamientos = models.PositiveSmallIntegerField(default=0)
    habitaciones = models.PositiveSmallIntegerField(default=0)
    banos = models.PositiveSmallIntegerField(default=0)
    direccion = models.CharField(max_length=100)
    precio_mensual = models.DecimalField(max_digits=8, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    region_codigo = models.CharField(max_length=10, blank=True, null=True)
    region_nombre = models.CharField(max_length=100, blank=True, null=True)
    comuna_codigo = models.CharField(max_length=10, blank=True, null=True)
    comuna_nombre = models.CharField(max_length=100, blank=True, null=True)
    tipo_inmueble = models.CharField(max_length=20, choices=Tipo_de_inmueble.choices)
    esta_publicado = models.BooleanField(default=False)
    
    class Meta:
        permissions = [
            ("gestionar_inmueble", "Puede gestionar inmuebles"),
            ("ver_todos_inmuebles", "Puede ver todos los inmuebles"),
            ("publicar_inmueble", "Puede publicar inmuebles"),
        ]
    
    def __str__(self):
        return f" {self.id} {self.propietario} {self.nombre}"
    
    @property
    def imagen_principal(self):
        """Devuelve la primera imagen como principal"""
        return self.imagenes.first().imagen if self.imagenes.exists() else None

class ImagenInmueble(models.Model):
    inmueble = models.ForeignKey(
        Inmueble, 
        on_delete=models.CASCADE, 
        related_name="imagenes"
    )
    imagen = models.ImageField(upload_to='inmuebles/galeria/')
    descripcion = models.CharField(max_length=200, blank=True)
    orden = models.PositiveIntegerField(default=0)  # Para ordenar imágenes
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'creado']

    def __str__(self):
        return f"Imagen de {self.inmueble.nombre}"


class SolicitudArriendo(models.Model):
    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = "P", _("Pendiente")
        ACEPTADA = "A", _("Aceptada")
        RECHAZADA = "R", _("Rechazada")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name="solicitudes")
    arrendatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="solicitudes_enviadas", null=True )
    mensaje = models.TextField(default="", blank=True)
    estado = models.CharField(max_length=10, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("gestionar_solicitud", "Puede gestionar solicitudes de arriendo"),
            ("aprobar_solicitud", "Puede aprobar/rechazar solicitudes"),
        ]

    def __str__(self):
        return f"{self.uuid} | {self.inmueble} | {self.estado}"

class PerfilUsuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ARRENDADOR = "ARRENDADOR", _("Arrendador")
        ARRENDATARIO = "ARRENDATARIO", _("Arrendatario")
        ADMINISTRADOR = "ADMINISTRADOR", _("Administrador")

    tipo_usuario = models.CharField(max_length=13, choices=TipoUsuario.choices, default=TipoUsuario.ARRENDATARIO)
    rut = models.CharField(max_length=50, unique=True, blank=True, null=True)
    imagen = models.ImageField(upload_to='foto_perfil/', default="default-profile.webp")
    
    # Campos adicionales para gestión
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ("gestionar_usuario", "Puede gestionar usuarios"),
            ("ver_todos_usuarios", "Puede ver todos los usuarios"),
        ]

    def __str__(self):
        return f"{self.get_full_name()} | {self.tipo_usuario}"

# Señal para crear grupos y permisos automáticamente después de las migraciones
@receiver(post_migrate)
def crear_grupos_y_permisos(sender, **kwargs):
    if sender.name != 'portal':
        return

"""
############################################################################
# Crear un grupo de Administradores
administradores_group, created = Group.objects.get_or_create(name='Administradores')
# Asignar permisos al grupo
permissions = Permission.objects.filter(codename__in=[
    'add_region', 'change_region', 'delete_region',
    'add_comuna', 'change_comuna', 'delete_comuna',
    'add_inmueble', 'change_inmueble', 'delete_inmueble',
    'add_solicitudarriendo', 'change_solicitudarriendo', 'delete_solicitudarriendo',
    'add_perfilusuario', 'change_perfilusuario', 'delete_perfilusuario',
])
administradores_group.permissions.set(permissions)

############################################################################    
# Crear un grupo de Arrendadores
arrendadores_group, created = Group.objects.get_or_create(name='Arrendadores')

# Asignar permisos al grupo
permission = Permission.objects.get(name='pueden agregar inmueble')
arrendadores_group.permissions.add(permission)

############################################################################
# Crear un grupo de Arrendatarios
arrendatarios_group, created = Group.objects.get_or_create(name='Arrendatarios')

# Asignar permisos al grupo
permission = Permission.objects.get(name='no pueden agregar inmueble')
arrendatarios_group.permissions.add(permission)
"""
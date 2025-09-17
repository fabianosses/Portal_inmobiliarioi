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
    imagen = models.ImageField(upload_to='inmuebles/', default='sin_imagen/')
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
    
    # Crear grupos por defecto con permisos específicos
    grupos_permisos = {
        'Administradores': [
            'portal.gestionar_region',
            'portal.gestionar_comuna',
            'portal.gestionar_inmueble',
            'portal.ver_todos_inmuebles',
            'portal.publicar_inmueble',
            'portal.gestionar_solicitud',
            'portal.aprobar_solicitud',
            'portal.gestionar_usuario',
            'portal.ver_todos_usuarios',
        ],
        'Arrendadores': [
            'portal.gestionar_inmueble',
            'portal.publicar_inmueble',
            'portal.gestionar_solicitud',
        ],
        'Arrendatarios': [
            'portal.ver_todos_inmuebles',
        ]
    }

  
    with transaction.atomic():
        for nombre_grupo, permisos in grupos_permisos.items():
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            
            # Limpiar permisos existentes antes de asignar nuevos para evitar duplicados
            # y asegurar que los permisos se actualicen si la lista de arriba cambia.
            grupo.permissions.clear()
            
            # Asignar permisos al grupo
            for codigo_permiso in permisos:
                try:
                    # Extraer el nombre del permiso del código completo
                    app_label, perm_codename = codigo_permiso.split('.', 1)
                    permiso = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=perm_codename
                    )
                    grupo.permissions.add(permiso)
                except Permission.DoesNotExist:
                    print(f"Permiso {codigo_permiso} no encontrado. Asegúrate de haber ejecutado las migraciones.")
            
            grupo.save()
        
        # Asignar usuarios a grupos según su tipo
        for usuario in PerfilUsuario.objects.all():
            usuario.groups.clear()  # Limpiar grupos existentes
            
            if usuario.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR:
                grupo = Group.objects.get(name='Administradores')
                usuario.groups.add(grupo)
            elif usuario.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDADOR:
                grupo = Group.objects.get(name='Arrendadores')
                usuario.groups.add(grupo)
            elif usuario.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDATARIO:
                grupo = Group.objects.get(name='Arrendatarios')
                usuario.groups.add(grupo)
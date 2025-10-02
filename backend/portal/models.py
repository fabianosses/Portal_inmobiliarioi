# backend/portal/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, User, Group, Permission
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import transaction 
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import uuid

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
    m2_construidos = models.FloatField(default=0, validators=[MinValueValidator(0)])
    m2_totales = models.FloatField(default=0, validators=[MinValueValidator(0)])
    estacionamientos = models.PositiveSmallIntegerField(default=0)
    habitaciones = models.PositiveSmallIntegerField(default=0)
    banos = models.PositiveSmallIntegerField(default=0)
    direccion = models.CharField(max_length=100)
    precio_mensual = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Precio mensual en pesos chilenos")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    region_codigo = models.CharField(max_length=15, blank=True, null=True, verbose_name='Código de Región')
    region_nombre = models.CharField(max_length=100, blank=True, null=True)
    comuna_codigo = models.CharField(max_length=15, blank=True, null=True, verbose_name='Código de Comuna')
    comuna_nombre = models.CharField(max_length=100, blank=True, null=True)
    tipo_inmueble = models.CharField(max_length=20, choices=Tipo_de_inmueble.choices)
    esta_publicado = models.BooleanField(default=False)

    class Meta:
        permissions = [
            # Para Arrendadores - pueden gestionar sus propios inmuebles
            ("agregar_inmueble", "Puede agregar inmuebles"),
            ("editar_propio_inmueble", "Puede editar sus propios inmuebles"),
            ("eliminar_propio_inmueble", "Puede eliminar sus propios inmuebles"),
            
            # Para Administradores - permisos globales
            ("ver_todos_inmuebles", "Puede ver todos los inmuebles"),
            ("editar_todos_inmuebles", "Puede editar todos los inmuebles"),
            ("eliminar_todos_inmuebles", "Puede eliminar todos los inmuebles"),
            ("publicar_inmueble", "Puede publicar/despublicar inmuebles"),
        ]
    
    def __str__(self):
        return f" {self.id} {self.propietario} {self.nombre}"

    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.m2_construidos > self.m2_totales:
            raise ValidationError({
                'm2_construidos': 'Los m² construidos no pueden ser mayores a los m² totales'
            })
        
        if self.precio_mensual and self.precio_mensual <= 0:
            raise ValidationError({
                'precio_mensual': 'El precio mensual debe ser mayor a 0'
            })
    
    def save(self, *args, **kwargs):
        self.clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def upload_to_inmuebles(instance, filename):
        """Función para generar rutas dinámicas para imágenes de inmuebles"""
        ext = filename.split('.')[-1]
        filename = f'{instance.nombre.replace(" ", "_")}_{instance.id}.{ext}'
        return f'inmuebles/{filename}'
    
    imagen = models.ImageField(
        upload_to=upload_to_inmuebles, 
        default='inmuebles/sin_imagen.jpg'
    )

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
    
    # Campos adicionales para gestión - HACER OPCIONALES
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)
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
    
    # Solo crear si no existen
    grupos_data = {
        'Administradores': [
            'ver_todos_inmuebles', 'editar_todos_inmuebles', 'eliminar_todos_inmuebles',
            'publicar_inmueble', 'gestionar_usuario', 'gestionar_region', 'gestionar_comuna',
            'gestionar_solicitud', 'aprobar_solicitud'
        ],
        'Arrendadores': [
            'agregar_inmueble', 'editar_propio_inmueble', 'eliminar_propio_inmueble'
        ],
        'Arrendatarios': [
            # Permisos básicos de visualización
        ]
    }
    
    for nombre_grupo, permisos_codenames in grupos_data.items():
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if created or kwargs.get('verbosity', 0) > 1:
            print(f"Grupo '{nombre_grupo}' {'creado' if created else 'ya existe'}")
            
        # Asignar permisos
        for codename in permisos_codenames:
            try:
                permiso = Permission.objects.get(
                    codename=codename, 
                    content_type__app_label='portal'
                )
                grupo.permissions.add(permiso)
            except Permission.DoesNotExist:
                if kwargs.get('verbosity', 0) > 1:
                    print(f"Permiso '{codename}' no encontrado para {nombre_grupo}")
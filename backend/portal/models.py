from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
import uuid

# Create your models here.

class Region(models.Model):
    nro_region = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nombre} ||| número de región es: {self.nro_region}" #Valparaiso ||| número de región es: V

class Comuna(models.Model):
    nombre = models.CharField(max_length=50)
    region = models.ForeignKey(Region,on_delete=models.PROTECT, related_name="comunas")

    def __str__(self):
        return f"{self.nombre} ||| número de región es: {self.region}" #Valparaiso ||| nombre de región es: Valparaiso
    

# modelo de inmueble
class Inmueble(models.Model):
    class Tipo_de_inmueble(models.TextChoices):
        casa = "CASA", _("Casa")
        depto = "DEPARTAMENTO", _("Departamento")
        parcela = "PARCELA", _("Parcela")

    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inmuebles")
    nombre = models.CharField(max_length=100)
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
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, related_name="inmuebles")

    tipo_inmueble = models.CharField(max_length=20, choices=Tipo_de_inmueble.choices)
#    estado_inmueble = models.CharField(max_length=20, choices=ESTADO_INMUEBLE_CHOICES)
    


    def __str__(self):
        return f"propietario: {self.propietario} | nombre: {self.nombre}"

"""    SolicitudArriendo:
        id (por defecto django)
        uuid
        arrendador
        inmueble
        choices
            aceptado
            rechazado
            pendiente
        creado
        actualizado
        mensaje
        archivos"""


class SolicitudArriendo(models.Model):

    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = "P", _("Pendiente")
        ACEPTADA = "A", _("Aceptada")
        RECHAZADA = "R", _("Rechazada")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name="solicitudes")
    arrendatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="solicitudes_enviadas")
    mensaje = models.TextField(default="", blank=True)
    estado = models.CharField(max_length=10, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uuid} | {self.inmueble} | {self.estado}"


class PerfilUsuario(AbstractUser):

    class TipoUsuario(models.TextChoices):
        ARRENDADOR = "ARRENDADOR", _("Arrendador")
        ARRENDATARIO = "ARRENDATARIO", _("Arrendatario")

#    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo_usuario = models.CharField(max_length=13, choices=TipoUsuario.choices, default=TipoUsuario.ARRENDATARIO)
    rut = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.user.get_full_name()} | {self.tipo_usuario}"
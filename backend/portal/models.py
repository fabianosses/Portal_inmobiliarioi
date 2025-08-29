from django.db import models
from django.utils.translation import gettext_lazy as _

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


    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    m2_construidos = models.FloatField()
    m2_totales = models.FloatField()
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
        return f"{self.get_tipo_inmueble_display()} en {self.direccion}, {self.comuna.nombre} - ${self.precio}"
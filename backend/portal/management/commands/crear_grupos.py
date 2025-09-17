# backend/portal/management/commands/crear_grupos.py

from django.core.management.base import BaseCommand
from django.db.models.signals import post_migrate
from portal.models import crear_grupos_y_permisos

class Command(BaseCommand):
    help = 'Crea o actualiza grupos de usuarios con permisos predefinidos'
    
    def handle(self, *args, **options):
        # Ejecutar la señal manualmente
        crear_grupos_y_permisos(None)
        
        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos creados/actualizados exitosamente')
        )
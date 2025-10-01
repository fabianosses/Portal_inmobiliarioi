# backend/portal/management/commands/crear_grupos.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from portal.models import PerfilUsuario
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Crear grupos y permisos iniciales para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando grupos y permisos...')
        
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
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{nombre_grupo}" creado')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{nombre_grupo}" ya existe')
                )
            
            # Asignar permisos
            permisos_agregados = 0
            for codename in permisos_codenames:
                try:
                    permiso = Permission.objects.get(
                        codename=codename, 
                        content_type__app_label='portal'
                    )
                    grupo.permissions.add(permiso)
                    permisos_agregados += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Permiso "{codename}" no encontrado')
                    )
            
            if permisos_agregados > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  - {permisos_agregados} permisos asignados')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos creados exitosamente')
        )
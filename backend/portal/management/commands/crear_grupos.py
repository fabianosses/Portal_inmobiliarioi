# backend/portal/management/commands/crear_grupos.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Crear grupos iniciales y asignar permisos'

    def handle(self, *args, **options):
        self.stdout.write('Creando grupos y permisos...')
        
        # Crear grupo de Administradores
        administradores_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            # Todos los permisos de portal
            portal_permissions = Permission.objects.filter(content_type__app_label='portal')
            administradores_group.permissions.set(portal_permissions)
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores" creado con todos los permisos'))
        
        # Crear grupo de Arrendadores
        arrendadores_group, created = Group.objects.get_or_create(name='Arrendadores')
        if created:
            # Permisos específicos para arrendadores
            permisos_arrendadores = Permission.objects.filter(
                codename__in=[
                    'add_inmueble', 'change_inmueble', 'delete_inmueble',
                    'agregar_inmueble', 'editar_propio_inmueble', 'eliminar_propio_inmueble'
                ]
            )
            arrendadores_group.permissions.set(permisos_arrendadores)
            self.stdout.write(self.style.SUCCESS('Grupo "Arrendadores" creado'))
        
        # Crear grupo de Arrendatarios
        arrendatarios_group, created = Group.objects.get_or_create(name='Arrendatarios')
        if created:
            # Solo permisos de visualización
            permisos_arrendatarios = Permission.objects.filter(
                codename__in=['view_inmueble', 'ver_todos_inmuebles']
            )
            arrendatarios_group.permissions.set(permisos_arrendatarios)
            self.stdout.write(self.style.SUCCESS('Grupo "Arrendatarios" creado'))
        
        self.stdout.write(self.style.SUCCESS('Proceso completado'))
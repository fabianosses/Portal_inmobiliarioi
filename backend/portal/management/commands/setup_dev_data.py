#backend/portal/management/commands/setup_dev_data.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from portal.models import Inmueble, SolicitudArriendo

class Command(BaseCommand):
    help = 'Clean database and setup complete development data'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning existing data...')
        
        # Limpiar datos existentes
        SolicitudArriendo.objects.all().delete()
        Inmueble.objects.all().delete()
        
        User = get_user_model()
        # Mantener el superusuario si existe, eliminar otros
        User.objects.exclude(is_superuser=True).delete()
        
        self.stdout.write('Loading fixtures...')
        
        # 1. Cargar fixtures
        call_command('loaddata', 'users')
        call_command('loaddata', 'inmuebles') 
        
        self.stdout.write(
            self.style.SUCCESS('Development data setup completed!')
        )
        self.stdout.write('Users created:')
        self.stdout.write('- admin / admin123 (Administrador)')
        self.stdout.write('- arrendador1 / arrendador123 (Arrendador)') 
        self.stdout.write('- arrendatario1 / arrendatario123 (Arrendatario)')
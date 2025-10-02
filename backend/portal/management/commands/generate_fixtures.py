from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
import json

class Command(BaseCommand):
    help = 'Generate fixture data with properly hashed passwords'

    def handle(self, *args, **options):
        # Generar password hasheado
        password = make_password('password123')  # Cambia por la contraseña que quieras
        
        self.stdout.write(f"Password hash generado: {password}")
        
        # Datos de ejemplo para users.json
        users_data = [
            {
                "model": "portal.perfilusuario",
                "pk": 1,
                "fields": {
                    "password": password,
                    "last_login": None,
                    "is_superuser": True,
                    "username": "admin",
                    "first_name": "Administrador",
                    "last_name": "Sistema",
                    "email": "admin@inmobiliaria.com",
                    "is_staff": True,
                    "is_active": True,
                    "date_joined": "2024-01-01T00:00:00Z",
                    "tipo_usuario": "ADMINISTRADOR",
                    "rut": "12345678-9",
                    "imagen": "foto_perfil/default-profile.webp",
                    "groups": [],
                    "user_permissions": []
                }
            }
        ]
        
        self.stdout.write("Ejecuta: python manage.py generate_fixtures")
        self.stdout.write("Luego copia el password hash en tu fixture users.json")
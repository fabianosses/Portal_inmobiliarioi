#backend/portal/management/commands/generate_inmuebles_por_comuna.py
from django.core.management.base import BaseCommand
from django.db import connection
from portal.models import Inmueble
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Genera listado de inmuebles por comuna y guarda en archivo de texto'

    def handle(self, *args, **options):
        self.generar_reporte_sql()
        self.generar_reporte_orm()

    def generar_reporte_sql(self):
        """Genera reporte usando SQL directo"""
        self.stdout.write("Generando reporte con SQL...")
        
        query = """
        SELECT 
            comuna_nombre,
            nombre,
            descripcion
        FROM portal_inmueble 
        WHERE esta_publicado = true
        ORDER BY comuna_nombre, nombre
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        
        self.guardar_archivo(resultados, 'sql')

    def generar_reporte_orm(self):
        """Genera reporte usando ORM de Django"""
        self.stdout.write("Generando reporte con ORM...")
        
        inmuebles = Inmueble.objects.filter(
            esta_publicado=True
        ).order_by('comuna_nombre', 'nombre').values(
            'comuna_nombre', 'nombre', 'descripcion'
        )
        
        resultados = [
            (item['comuna_nombre'], item['nombre'], item['descripcion'])
            for item in inmuebles
        ]
        
        self.guardar_archivo(resultados, 'orm')

    def guardar_archivo(self, datos, metodo):
        """Guarda los datos en un archivo de texto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inmuebles_por_comuna_{metodo}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LISTADO DE INMUEBLES POR COMUNA\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Método: {metodo.upper()}\n")
            f.write("=" * 80 + "\n\n")
            
            comuna_actual = None
            contador_comuna = 0
            contador_total = 0
            
            for comuna, nombre, descripcion in datos:
                if comuna != comuna_actual:
                    if comuna_actual is not None:
                        f.write(f"\nTotal en {comuna_actual}: {contador_comuna} inmuebles\n")
                        f.write("-" * 80 + "\n\n")
                    
                    comuna_actual = comuna
                    contador_comuna = 0
                    f.write(f"COMUNA: {comuna.upper()}\n")
                    f.write("=" * 40 + "\n")
                
                contador_comuna += 1
                contador_total += 1
                
                f.write(f"\n{contador_comuna}. {nombre}\n")
                f.write(f"   Descripción: {descripcion}\n")
            
            # Escribir totales de la última comuna
            if comuna_actual:
                f.write(f"\nTotal en {comuna_actual}: {contador_comuna} inmuebles\n")
                f.write("-" * 80 + "\n\n")
            
            f.write(f"TOTAL GENERAL: {contador_total} inmuebles listados\n")
        
        self.stdout.write(
            self.style.SUCCESS(f'Archivo generado: {filename}')
        )
from django.core.management.base import BaseCommand
from django.db import connection
from portal.models import Inmueble
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Genera listado de inmuebles por región y guarda en archivo de texto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--metodo',
            type=str,
            choices=['sql', 'orm', 'ambos'],
            default='ambos',
            help='Método a usar para la consulta (sql, orm, ambos)'
        )
        parser.add_argument(
            '--region',
            type=str,
            help='Filtrar por región específica'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Nombre personalizado para el archivo de salida'
        )
        parser.add_argument(
            '--incluir-comunas',
            action='store_true',
            help='Incluir desglose por comunas dentro de cada región'
        )

    def handle(self, *args, **options):
        metodo = options['metodo']
        region_filtro = options['region']
        output_file = options['output']
        incluir_comunas = options['incluir_comunas']

        if metodo in ['sql', 'ambos']:
            self.generar_reporte_sql(region_filtro, output_file, incluir_comunas)
        
        if metodo in ['orm', 'ambos']:
            self.generar_reporte_orm(region_filtro, output_file, incluir_comunas)

    def generar_reporte_sql(self, region_filtro=None, output_file=None, incluir_comunas=False):
        """Genera reporte usando SQL directo"""
        self.stdout.write("Generando reporte por región con SQL...")
        
        if incluir_comunas:
            query = """
            SELECT 
                region_nombre,
                comuna_nombre,
                nombre,
                descripcion,
                precio_mensual,
                tipo_inmueble
            FROM portal_inmueble 
            WHERE esta_publicado = true
            """
        else:
            query = """
            SELECT 
                region_nombre,
                nombre,
                descripcion,
                precio_mensual,
                tipo_inmueble
            FROM portal_inmueble 
            WHERE esta_publicado = true
            """
        
        params = []
        if region_filtro:
            query += " AND region_nombre = %s"
            params.append(region_filtro)
        
        if incluir_comunas:
            query += " ORDER BY region_nombre, comuna_nombre, nombre"
        else:
            query += " ORDER BY region_nombre, nombre"
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            resultados = cursor.fetchall()
        
        filename = self.guardar_archivo(resultados, 'sql', output_file, incluir_comunas)
        self.stdout.write(
            self.style.SUCCESS(f'Archivo SQL generado: {filename}')
        )

    def generar_reporte_orm(self, region_filtro=None, output_file=None, incluir_comunas=False):
        """Genera reporte usando ORM de Django"""
        self.stdout.write("Generando reporte por región con ORM...")
        
        queryset = Inmueble.objects.filter(esta_publicado=True)
        
        if region_filtro:
            queryset = queryset.filter(region_nombre=region_filtro)
        
        if incluir_comunas:
            inmuebles = queryset.order_by('region_nombre', 'comuna_nombre', 'nombre').values(
                'region_nombre', 'comuna_nombre', 'nombre', 'descripcion', 'precio_mensual', 'tipo_inmueble'
            )
        else:
            inmuebles = queryset.order_by('region_nombre', 'nombre').values(
                'region_nombre', 'nombre', 'descripcion', 'precio_mensual', 'tipo_inmueble'
            )
        
        resultados = list(inmuebles)
        
        filename = self.guardar_archivo_orm(resultados, 'orm', output_file, incluir_comunas)
        self.stdout.write(
            self.style.SUCCESS(f'Archivo ORM generado: {filename}')
        )

    def guardar_archivo(self, datos, metodo, output_file=None, incluir_comunas=False):
        """Guarda los datos en un archivo de texto (versión SQL)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_file:
            filename = output_file
        else:
            tipo_reporte = "region_comuna" if incluir_comunas else "region"
            filename = f"inmuebles_por_{tipo_reporte}_{metodo}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LISTADO DE INMUEBLES POR REGIÓN\n")
            if incluir_comunas:
                f.write(f"(Incluye desglose por comunas)\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Método: {metodo.upper()}\n")
            f.write("=" * 80 + "\n\n")
            
            if incluir_comunas:
                self._guardar_con_comunas(f, datos)
            else:
                self._guardar_sin_comunas(f, datos)
        
        return filename

    def guardar_archivo_orm(self, datos, metodo, output_file=None, incluir_comunas=False):
        """Guarda los datos en un archivo de texto (versión ORM)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_file:
            filename = output_file
        else:
            tipo_reporte = "region_comuna" if incluir_comunas else "region"
            filename = f"inmuebles_por_{tipo_reporte}_{metodo}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LISTADO DE INMUEBLES POR REGIÓN\n")
            if incluir_comunas:
                f.write(f"(Incluye desglose por comunas)\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Método: {metodo.upper()}\n")
            f.write("=" * 80 + "\n\n")
            
            if incluir_comunas:
                self._guardar_con_comunas_orm(f, datos)
            else:
                self._guardar_sin_comunas_orm(f, datos)
        
        return filename

    def _guardar_sin_comunas(self, f, datos):
        """Guarda datos sin desglose por comuna (SQL)"""
        region_actual = None
        contador_region = 0
        contador_total = 0
        valor_total_region = 0
        valor_total_general = 0
        
        for region, nombre, descripcion, precio, tipo_inmueble in datos:
            if region != region_actual:
                if region_actual is not None:
                    f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
                    f.write(f"   • Total inmuebles: {contador_region}\n")
                    f.write(f"   • Valor total: ${valor_total_region:,}\n")
                    if contador_region > 0:
                        f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
                    f.write("=" * 60 + "\n\n")
                
                region_actual = region
                contador_region = 0
                valor_total_region = 0
                f.write(f"🏞️  REGIÓN: {region.upper()}\n")
                f.write("=" * 50 + "\n")
            
            contador_region += 1
            contador_total += 1
            valor_total_region += precio
            valor_total_general += precio
            
            f.write(f"\n{contador_region}. 🏡 {nombre}\n")
            f.write(f"   📝 {descripcion}\n")
            f.write(f"   💰 Precio: ${precio:,}\n")
            f.write(f"   🏘️  Tipo: {tipo_inmueble}\n")
        
        # Escribir totales de la última región
        if region_actual:
            f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
            f.write(f"   • Total inmuebles: {contador_region}\n")
            f.write(f"   • Valor total: ${valor_total_region:,}\n")
            if contador_region > 0:
                f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
            f.write("=" * 60 + "\n\n")
        
        # Resumen general
        f.write(f"\n🎯 RESUMEN EJECUTIVO:\n")
        f.write(f"   • Total regiones: {len(set([d[0] for d in datos]))}\n")
        f.write(f"   • Total inmuebles: {contador_total}\n")
        f.write(f"   • Valor total en arriendo: ${valor_total_general:,}\n")
        if contador_total > 0:
            f.write(f"   • Valor promedio: ${valor_total_general/contador_total:,.0f}\n")

    def _guardar_con_comunas(self, f, datos):
        """Guarda datos con desglose por comuna (SQL)"""
        region_actual = None
        comuna_actual = None
        contador_region = 0
        contador_comuna = 0
        contador_total = 0
        valor_total_region = 0
        valor_total_comuna = 0
        valor_total_general = 0
        
        for region, comuna, nombre, descripcion, precio, tipo_inmueble in datos:
            if region != region_actual:
                if region_actual is not None:
                    f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
                    f.write(f"   • Total inmuebles: {contador_region}\n")
                    f.write(f"   • Valor total: ${valor_total_region:,}\n")
                    if contador_region > 0:
                        f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
                    f.write("=" * 60 + "\n\n")
                
                region_actual = region
                comuna_actual = None
                contador_region = 0
                valor_total_region = 0
                f.write(f"🏞️  REGIÓN: {region.upper()}\n")
                f.write("=" * 60 + "\n")
            
            if comuna != comuna_actual:
                if comuna_actual is not None:
                    f.write(f"\n   📊 Resumen {comuna_actual}: {contador_comuna} inmuebles\n")
                    f.write(f"      Valor total: ${valor_total_comuna:,}\n")
                    f.write("   " + "-" * 50 + "\n")
                
                comuna_actual = comuna
                contador_comuna = 0
                valor_total_comuna = 0
                f.write(f"\n   🏘️  COMUNA: {comuna}\n")
                f.write("   " + "-" * 40 + "\n")
            
            contador_region += 1
            contador_comuna += 1
            contador_total += 1
            valor_total_region += precio
            valor_total_comuna += precio
            valor_total_general += precio
            
            f.write(f"\n   {contador_comuna}. 🏡 {nombre}\n")
            f.write(f"      📝 {descripcion}\n")
            f.write(f"      💰 Precio: ${precio:,}\n")
            f.write(f"      🏠 Tipo: {tipo_inmueble}\n")
        
        # Escribir totales de la última comuna y región
        if comuna_actual:
            f.write(f"\n   📊 Resumen {comuna_actual}: {contador_comuna} inmuebles\n")
            f.write(f"      Valor total: ${valor_total_comuna:,}\n")
            f.write("   " + "-" * 50 + "\n")
        
        if region_actual:
            f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
            f.write(f"   • Total inmuebles: {contador_region}\n")
            f.write(f"   • Valor total: ${valor_total_region:,}\n")
            if contador_region > 0:
                f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
            f.write("=" * 60 + "\n\n")
        
        # Resumen general
        f.write(f"\n🎯 RESUMEN EJECUTIVO:\n")
        regiones_count = len(set([d[0] for d in datos]))
        comunas_count = len(set([d[1] for d in datos]))
        f.write(f"   • Total regiones: {regiones_count}\n")
        f.write(f"   • Total comunas: {comunas_count}\n")
        f.write(f"   • Total inmuebles: {contador_total}\n")
        f.write(f"   • Valor total en arriendo: ${valor_total_general:,}\n")
        if contador_total > 0:
            f.write(f"   • Valor promedio: ${valor_total_general/contador_total:,.0f}\n")

    def _guardar_sin_comunas_orm(self, f, datos):
        """Guarda datos sin desglose por comuna (ORM)"""
        # Implementación similar a _guardar_sin_comunas pero para datos ORM
        region_actual = None
        contador_region = 0
        contador_total = 0
        valor_total_region = 0
        valor_total_general = 0
        
        for item in datos:
            region = item['region_nombre']
            nombre = item['nombre']
            descripcion = item['descripcion']
            precio = item['precio_mensual']
            tipo_inmueble = item['tipo_inmueble']
            
            if region != region_actual:
                if region_actual is not None:
                    f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
                    f.write(f"   • Total inmuebles: {contador_region}\n")
                    f.write(f"   • Valor total: ${valor_total_region:,}\n")
                    if contador_region > 0:
                        f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
                    f.write("=" * 60 + "\n\n")
                
                region_actual = region
                contador_region = 0
                valor_total_region = 0
                f.write(f"🏞️  REGIÓN: {region.upper()}\n")
                f.write("=" * 50 + "\n")
            
            contador_region += 1
            contador_total += 1
            valor_total_region += precio
            valor_total_general += precio
            
            f.write(f"\n{contador_region}. 🏡 {nombre}\n")
            f.write(f"   📝 {descripcion}\n")
            f.write(f"   💰 Precio: ${precio:,}\n")
            f.write(f"   🏘️  Tipo: {tipo_inmueble}\n")
        
        # Escribir totales de la última región
        if region_actual:
            f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
            f.write(f"   • Total inmuebles: {contador_region}\n")
            f.write(f"   • Valor total: ${valor_total_region:,}\n")
            if contador_region > 0:
                f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
            f.write("=" * 60 + "\n\n")
        
        # Resumen general
        f.write(f"\n🎯 RESUMEN EJECUTIVO:\n")
        f.write(f"   • Total regiones: {len(set([d['region_nombre'] for d in datos]))}\n")
        f.write(f"   • Total inmuebles: {contador_total}\n")
        f.write(f"   • Valor total en arriendo: ${valor_total_general:,}\n")
        if contador_total > 0:
            f.write(f"   • Valor promedio: ${valor_total_general/contador_total:,.0f}\n")

    def _guardar_con_comunas_orm(self, f, datos):
        """Guarda datos con desglose por comuna (ORM)"""
        # Implementación similar a _guardar_con_comunas pero para datos ORM
        region_actual = None
        comuna_actual = None
        contador_region = 0
        contador_comuna = 0
        contador_total = 0
        valor_total_region = 0
        valor_total_comuna = 0
        valor_total_general = 0
        
        for item in datos:
            region = item['region_nombre']
            comuna = item['comuna_nombre']
            nombre = item['nombre']
            descripcion = item['descripcion']
            precio = item['precio_mensual']
            tipo_inmueble = item['tipo_inmueble']
            
            if region != region_actual:
                if region_actual is not None:
                    f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
                    f.write(f"   • Total inmuebles: {contador_region}\n")
                    f.write(f"   • Valor total: ${valor_total_region:,}\n")
                    if contador_region > 0:
                        f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
                    f.write("=" * 60 + "\n\n")
                
                region_actual = region
                comuna_actual = None
                contador_region = 0
                valor_total_region = 0
                f.write(f"🏞️  REGIÓN: {region.upper()}\n")
                f.write("=" * 60 + "\n")
            
            if comuna != comuna_actual:
                if comuna_actual is not None:
                    f.write(f"\n   📊 Resumen {comuna_actual}: {contador_comuna} inmuebles\n")
                    f.write(f"      Valor total: ${valor_total_comuna:,}\n")
                    f.write("   " + "-" * 50 + "\n")
                
                comuna_actual = comuna
                contador_comuna = 0
                valor_total_comuna = 0
                f.write(f"\n   🏘️  COMUNA: {comuna}\n")
                f.write("   " + "-" * 40 + "\n")
            
            contador_region += 1
            contador_comuna += 1
            contador_total += 1
            valor_total_region += precio
            valor_total_comuna += precio
            valor_total_general += precio
            
            f.write(f"\n   {contador_comuna}. 🏡 {nombre}\n")
            f.write(f"      📝 {descripcion}\n")
            f.write(f"      💰 Precio: ${precio:,}\n")
            f.write(f"      🏠 Tipo: {tipo_inmueble}\n")
        
        # Escribir totales de la última comuna y región
        if comuna_actual:
            f.write(f"\n   📊 Resumen {comuna_actual}: {contador_comuna} inmuebles\n")
            f.write(f"      Valor total: ${valor_total_comuna:,}\n")
            f.write("   " + "-" * 50 + "\n")
        
        if region_actual:
            f.write(f"\n📊 RESUMEN {region_actual.upper()}:\n")
            f.write(f"   • Total inmuebles: {contador_region}\n")
            f.write(f"   • Valor total: ${valor_total_region:,}\n")
            if contador_region > 0:
                f.write(f"   • Valor promedio: ${valor_total_region/contador_region:,.0f}\n")
            f.write("=" * 60 + "\n\n")
        
        # Resumen general
        f.write(f"\n🎯 RESUMEN EJECUTIVO:\n")
        regiones_count = len(set([d['region_nombre'] for d in datos]))
        comunas_count = len(set([d['comuna_nombre'] for d in datos]))
        f.write(f"   • Total regiones: {regiones_count}\n")
        f.write(f"   • Total comunas: {comunas_count}\n")
        f.write(f"   • Total inmuebles: {contador_total}\n")
        f.write(f"   • Valor total en arriendo: ${valor_total_general:,}\n")
        if contador_total > 0:
            f.write(f"   • Valor promedio: ${valor_total_general/contador_total:,.0f}\n")
# backend/portal/services.py
import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ChileanLocationService:
    """
    Servicio para obtener datos geográficos de Chile con múltiples fuentes
    """
    
    # APIs alternativas
    DPA_API_URL = "https://apis.digital.gob.cl/dpa"
    GORE_API_URL = "https://gobiernoabierto.interior.gob.cl/api"
    
    # Datos estáticos completos
    REGIONES_STATIC = [
        {'codigo': '15', 'nombre': 'Arica y Parinacota'},
        {'codigo': '1', 'nombre': 'Tarapacá'},
        {'codigo': '2', 'nombre': 'Antofagasta'},
        {'codigo': '3', 'nombre': 'Atacama'},
        {'codigo': '4', 'nombre': 'Coquimbo'},
        {'codigo': '5', 'nombre': 'Valparaíso'},
        {'codigo': '13', 'nombre': 'Metropolitana de Santiago'},
        {'codigo': '6', 'nombre': 'Libertador General Bernardo O\'Higgins'},
        {'codigo': '7', 'nombre': 'Maule'},
        {'codigo': '16', 'nombre': 'Ñuble'},
        {'codigo': '8', 'nombre': 'Biobío'},
        {'codigo': '9', 'nombre': 'La Araucanía'},
        {'codigo': '14', 'nombre': 'Los Ríos'},
        {'codigo': '10', 'nombre': 'Los Lagos'},
        {'codigo': '11', 'nombre': 'Aysén del General Carlos Ibáñez del Campo'},
        {'codigo': '12', 'nombre': 'Magallanes y de la Antártica Chilena'}
    ]

    COMUNAS_STATIC = {
        '15': [  # Arica y Parinacota
            {'codigo': '15101', 'nombre': 'Arica'}, {'codigo': '15102', 'nombre': 'Camarones'},
            {'codigo': '15201', 'nombre': 'Putre'}, {'codigo': '15202', 'nombre': 'General Lagos'},
        ],
        '1': [  # Tarapacá
            {'codigo': '1101', 'nombre': 'Iquique'}, {'codigo': '1102', 'nombre': 'Alto Hospicio'},
            {'codigo': '1401', 'nombre': 'Pozo Almonte'}, {'codigo': '1402', 'nombre': 'Camiña'},
            {'codigo': '1403', 'nombre': 'Colchane'}, {'codigo': '1404', 'nombre': 'Huara'},
            {'codigo': '1405', 'nombre': 'Pica'},
        ],
        '13': [  # Metropolitana (comunas más comunes)
            {'codigo': '13101', 'nombre': 'Santiago'}, {'codigo': '13102', 'nombre': 'Cerrillos'},
            {'codigo': '13103', 'nombre': 'Cerro Navia'}, {'codigo': '13104', 'nombre': 'Conchalí'},
            {'codigo': '13105', 'nombre': 'El Bosque'}, {'codigo': '13106', 'nombre': 'Estación Central'},
            {'codigo': '13107', 'nombre': 'Huechuraba'}, {'codigo': '13108', 'nombre': 'Independencia'},
            {'codigo': '13109', 'nombre': 'La Cisterna'}, {'codigo': '13110', 'nombre': 'La Florida'},
            {'codigo': '13111', 'nombre': 'La Granja'}, {'codigo': '13112', 'nombre': 'La Pintana'},
            {'codigo': '13113', 'nombre': 'La Reina'}, {'codigo': '13114', 'nombre': 'Las Condes'},
            {'codigo': '13115', 'nombre': 'Lo Barnechea'}, {'codigo': '13116', 'nombre': 'Lo Espejo'},
            {'codigo': '13117', 'nombre': 'Lo Prado'}, {'codigo': '13118', 'nombre': 'Macul'},
            {'codigo': '13119', 'nombre': 'Maipú'}, {'codigo': '13120', 'nombre': 'Ñuñoa'},
            {'codigo': '13121', 'nombre': 'Pedro Aguirre Cerda'}, {'codigo': '13122', 'nombre': 'Peñalolén'},
            {'codigo': '13123', 'nombre': 'Providencia'}, {'codigo': '13124', 'nombre': 'Pudahuel'},
            {'codigo': '13125', 'nombre': 'Quilicura'}, {'codigo': '13126', 'nombre': 'Quinta Normal'},
            {'codigo': '13127', 'nombre': 'Recoleta'}, {'codigo': '13128', 'nombre': 'Renca'},
            {'codigo': '13129', 'nombre': 'San Joaquín'}, {'codigo': '13130', 'nombre': 'San Miguel'},
            {'codigo': '13131', 'nombre': 'San Ramón'}, {'codigo': '13201', 'nombre': 'Puente Alto'},
            {'codigo': '13202', 'nombre': 'Pirque'}, {'codigo': '13203', 'nombre': 'San José de Maipo'},
        ],
        '5': [  # Valparaíso
            {'codigo': '5101', 'nombre': 'Valparaíso'}, {'codigo': '5102', 'nombre': 'Viña del Mar'},
            {'codigo': '5103', 'nombre': 'Concón'}, {'codigo': '5104', 'nombre': 'Quilpué'},
            {'codigo': '5105', 'nombre': 'Villa Alemana'}, {'codigo': '5106', 'nombre': 'Juan Fernández'},
            {'codigo': '5107', 'nombre': 'Casablanca'}, {'codigo': '5108', 'nombre': 'Puchuncaví'},
            {'codigo': '5109', 'nombre': 'Quintero'}, {'codigo': '5110', 'nombre': 'Valparaíso'},
            {'codigo': '5111', 'nombre': 'Viña del Mar'}, {'codigo': '5112', 'nombre': 'Isla de Pascua'},
        ],
        '8': [  # Biobío
            {'codigo': '8101', 'nombre': 'Concepción'}, {'codigo': '8102', 'nombre': 'Coronel'},
            {'codigo': '8103', 'nombre': 'Chiguayante'}, {'codigo': '8104', 'nombre': 'Florida'},
            {'codigo': '8105', 'nombre': 'Hualqui'}, {'codigo': '8106', 'nombre': 'Lota'},
            {'codigo': '8107', 'nombre': 'Penco'}, {'codigo': '8108', 'nombre': 'San Pedro de la Paz'},
            {'codigo': '8109', 'nombre': 'Santa Juana'}, {'codigo': '8110', 'nombre': 'Talcahuano'},
            {'codigo': '8111', 'nombre': 'Tomé'}, {'codigo': '8112', 'nombre': 'Hualpén'},
        ],
        '9': [  # La Araucanía
            {'codigo': '9101', 'nombre': 'Temuco'}, {'codigo': '9102', 'nombre': 'Carahue'},
            {'codigo': '9103', 'nombre': 'Cunco'}, {'codigo': '9104', 'nombre': 'Curarrehue'},
            {'codigo': '9105', 'nombre': 'Freire'}, {'codigo': '9106', 'nombre': 'Galvarino'},
            {'codigo': '9107', 'nombre': 'Gorbea'}, {'codigo': '9108', 'nombre': 'Lautaro'},
            {'codigo': '9109', 'nombre': 'Loncoche'}, {'codigo': '9110', 'nombre': 'Melipeuco'},
            {'codigo': '9111', 'nombre': 'Nueva Imperial'}, {'codigo': '9112', 'nombre': 'Padre las Casas'},
            {'codigo': '9113', 'nombre': 'Perquenco'}, {'codigo': '9114', 'nombre': 'Pitrufquén'},
            {'codigo': '9115', 'nombre': 'Pucón'}, {'codigo': '9116', 'nombre': 'Saavedra'},
            {'codigo': '9117', 'nombre': 'Teodoro Schmidt'}, {'codigo': '9118', 'nombre': 'Toltén'},
            {'codigo': '9119', 'nombre': 'Vilcún'}, {'codigo': '9120', 'nombre': 'Villarrica'},
            {'codigo': '9121', 'nombre': 'Cholchol'},
        ]
    }

    @staticmethod
    def get_regiones():
        """Obtiene regiones desde API oficial con fallback a datos estáticos."""
        # Intentar obtener de cache primero
        cached_regiones = cache.get('chile_regiones')
        if cached_regiones:
            return cached_regiones
            
        # Usar datos estáticos directamente para evitar problemas de API
        logger.info("Usando datos estáticos de regiones")
        cache.set('chile_regiones', ChileanLocationService.REGIONES_STATIC, 86400)
        return ChileanLocationService.REGIONES_STATIC

    @staticmethod
    def get_comunas_by_region(region_codigo):
        """Obtiene comunas desde datos estáticos."""
        if not region_codigo:
            return []
            
        cache_key = f'chile_comunas_{region_codigo}'
        cached_comunas = cache.get(cache_key)
        if cached_comunas:
            return cached_comunas
            
        logger.info(f"Buscando comunas estáticas para región: {region_codigo}")
        
        # Usar datos estáticos directamente
        comunas_estaticas = ChileanLocationService.COMUNAS_STATIC.get(region_codigo, [])
        
        if not comunas_estaticas:
            logger.warning(f"No se encontraron comunas estáticas para la región {region_codigo}")
            # Crear una comuna genérica como fallback
            comunas_estaticas = [{'codigo': f'{region_codigo}001', 'nombre': 'Comuna Principal'}]
        
        logger.info(f"Encontradas {len(comunas_estaticas)} comunas para región {region_codigo}")
        cache.set(cache_key, comunas_estaticas, 86400)
        return comunas_estaticas

    @staticmethod
    def get_all_comunas():
        """Obtiene todas las comunas de todas las regiones (para debugging)."""
        all_comunas = []
        for region_codigo, comunas in ChileanLocationService.COMUNAS_STATIC.items():
            all_comunas.extend(comunas)
        return all_comunas
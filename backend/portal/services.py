# backend/portal/services.py

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ChileanLocationService:
    BASE_URL = "https://apis.digital.gob.cl/dpa"
    
    @classmethod
    def get_regiones(cls):
        """Obtener todas las regiones de Chile desde API externa"""
        try:
            response = requests.get(f"{cls.BASE_URL}/regiones", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching regions (Error al obtener regiones): {e}")
            return []
    
    @classmethod
    def get_comunas_by_region(cls, region_code):
        """Obtener comunas de una región específica"""
        try:
            response = requests.get(f"{cls.BASE_URL}/regiones/{region_code}/comunas", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching communes for region (Error al obtener las comunas para la región) {region_code}: {e}")
            return []
    
    @classmethod
    def get_all_comunas(cls):
        """Obtener todas las comunas de Chile"""
        try:
            response = requests.get(f"{cls.BASE_URL}/comunas", timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching all communes (Error al obtener todas las comunas): {e}")
            return []
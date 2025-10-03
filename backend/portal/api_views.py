# backend/portal/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .services import ChileanLocationService

@method_decorator(csrf_exempt, name='dispatch')
class RegionAPIView(View):
    """API View para obtener regiones de Chile"""
    
    def get(self, request):
        regiones = ChileanLocationService.get_regiones()
        return JsonResponse(regiones, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class ComunaAPIView(View):
    """API View para obtener comunas de Chile"""
    
    def get(self, request):
        region_code = request.GET.get('region')
        
        if region_code:
            comunas = ChileanLocationService.get_comunas_by_region(region_code)
        else:
            comunas = ChileanLocationService.get_all_comunas()
        
        return JsonResponse(comunas, safe=False)
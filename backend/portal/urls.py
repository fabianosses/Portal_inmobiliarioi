from django.urls import path
from .views import *


urlpatterns = [
    path('listar_regiones/', RegionListView.as_view(), name='region_list'),
    path('crear_region/', RegionCreateView.as_view(), name='region_create'),
    path('actualizar_region/<int:pk>/', RegionUpdateView.as_view(), name='actualizar_region'),
    path('eliminar_region/<int:pk>/', RegionDeleteView.as_view(), name='eliminar_region'),
##########################################################
    path('listar_comunas/', ComunaListView.as_view(), name='comuna_list'),
    path('crear_comuna/', ComunaCreateView.as_view(), name='comuna_create'),
    path('actualizar_comuna/<int:pk>/', ComunaUpdateView.as_view(), name='actualizar_comuna'),
    path('eliminar_comuna/<int:pk>/', ComunaDeleteView.as_view(), name='eliminar_comuna'),
##########################################################
    path('listar_inmuebles/', InmuebleListView.as_view(), name='inmueble_list'),
    path('crear_inmueble/', InmuebleCreateView.as_view(), name='inmueble_create'),
    path('actualizar_inmueble/<int:pk>/', InmuebleUpdateView.as_view(), name='actualizar_inmueble'),
    path('eliminar_inmueble/<int:pk>/', InmuebleDeleteView.as_view(), name='eliminar_inmueble'),
]
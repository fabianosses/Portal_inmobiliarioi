# backend/portal/urls.py

from django.urls import path
from django.views.generic import RedirectView
from .api_views import RegionAPIView, ComunaAPIView
from .views import (
    cargar_comunas,
    SolicitudArriendoCreateView,
    PerfilView, PerfilUserUpdateView,
    CustomLoginView, CustomLogoutView,
    register_view,
    InmueblesListView,
    InmuebleCreateView,
    InmuebleUpdateView,
    InmuebleDeleteView,
    RegionListView,
    RegionCreateView,
    RegionUpdateView,
    RegionDeleteView,
    ComunaListView,
    ComunaCreateView,
    ComunaUpdateView,
    ComunaDeleteView,
    SolicitudArriendoListView,
    SolicitudArriendoUpdateView,
    SolicitudArriendoDeleteView,
    GrupoListView, 
    GrupoUpdateView, 
    UsuarioGrupoUpdateView,
    forzar_actualizacion_grupos,
    home_view,
    UsuarioListView,
)

urlpatterns = [

    path('', home_view, name='home'),

    # region
    path('listar_regiones/', RegionListView.as_view(), name='region_list'),
    path('crear_region/', RegionCreateView.as_view(), name='region_create'),
    path('actualizar_region/<int:pk>/', RegionUpdateView.as_view(), name='actualizar_region'),
    path('borrar_region/<int:pk>/', RegionDeleteView.as_view(), name='borrar_region'),
##########################################################
    
    # comuna
    path('listar_comunas/', ComunaListView.as_view(), name='comuna_list'),
    path('crear_comuna/', ComunaCreateView.as_view(), name='comuna_create'),
    path('actualizar_comuna/<int:pk>/', ComunaUpdateView.as_view(), name='comuna_update'),
    path('borrar_comuna/<int:pk>/', ComunaDeleteView.as_view(), name='borrar_comuna'),
##########################################################

    # inmueble
    path('listar_inmuebles/', InmueblesListView.as_view(), name='inmueble_list'),
    path('crear_inmueble/', InmuebleCreateView.as_view(), name='inmueble_create'),
    path('actualizar_inmueble/<int:pk>/', InmuebleUpdateView.as_view(), name='actualizar_inmueble'),
    path('borrar_inmueble/<int:pk>/', InmuebleDeleteView.as_view(), name='borrar_inmueble'),
##########################################################

    # solicitud arriendo
    path('listar_solicitudes/', SolicitudArriendoListView.as_view(), name='solicitud_list'),
    path('crear_solicitud/', SolicitudArriendoCreateView.as_view(), name='solicitud_create'),
    path('actualizar_solicitud/<int:pk>/', SolicitudArriendoUpdateView.as_view(), name='solicitud_update'),
    path('borrar_solicitud/<int:pk>/', SolicitudArriendoDeleteView.as_view(), name='solicitud_delete'),
##########################################################

    # perfil usuario
    path('actualizar_perfil/<int:pk>', PerfilUserUpdateView.as_view(), name='perfil_update'),
    path('perfil/', PerfilView.as_view(), name='perfil'),

#########################################################################
    # autenticación
    path('account/', RedirectView.as_view(url='/account/register/', permanent=False)),
    path('account/login/', CustomLoginView.as_view(), name='login'),
    path('account/logout/', CustomLogoutView.as_view(), name='logout'),
    path('account/register/', register_view, name='register'),

#########################################################################
    # API endpoints
    path('api/regiones/', RegionAPIView.as_view(), name='api_regiones'),
    path('api/comunas/', ComunaAPIView.as_view(), name='api_comunas'),

#########################################################################
    # Cargar comunas dinámicamente
    path('cargar-comunas/', cargar_comunas, name='cargar_comunas'),

#########################################################################
    # URLs para gestión de grupos
    path('grupos/', GrupoListView.as_view(), name='grupo_list'),
    path('grupos/<int:pk>/editar/', GrupoUpdateView.as_view(), name='grupo_update'),
    path('usuarios/<int:pk>/grupos/', UsuarioGrupoUpdateView.as_view(), name='usuario_grupo_update'),
    path('grupos/forzar-actualizacion/', forzar_actualizacion_grupos, name='forzar_actualizacion_grupos'),
]
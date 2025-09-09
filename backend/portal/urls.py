from django.urls import path
from .views import (
    HomeInmuebleListView,
    SolicitudArriendoCreateView,
    PerfilView, PerfilUserUpdateView,
    login_view, logout_view, register_view,
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
    PerfilUserUpdateView
)

urlpatterns = [

    path('', InmueblesListView.as_view(), name='home'),

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
    path('account/login/', login_view, name='login'),
    path('account/logout/', logout_view, name='logout'),
    path('account/register/', register_view, name='register'),
]
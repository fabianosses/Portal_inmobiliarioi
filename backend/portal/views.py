# backend/portal/views.py

from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .services import ChileanLocationService
from .mixins import (
    PermisoRequeridoMixin, PuedeGestionarInmueblesMixin, PuedeVerTodosInmueblesMixin,
    PuedeGestionarSolicitudesMixin, PuedeAprobarSolicitudesMixin, PuedeGestionarUsuariosMixin,
    PuedeGestionarRegionesMixin, PuedeGestionarComunasMixin, EsAdministradorMixin,
    EsArrendadorMixin, EsArrendatarioMixin
)

from .models import (
    Region,
    Comuna,
    Inmueble,
    SolicitudArriendo,
    PerfilUsuario
)

from .forms import (
    RegionForm,
    ComunaForm,
    InmuebleForm,
    SolicitudArriendoForm,
    PerfilUsuarioForm
)

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

def cargar_comunas(request):
    """Vista para cargar comunas basado en la región seleccionada"""
    region_code = request.GET.get('region')
    if region_code:
        comunas = ChileanLocationService.get_comunas_by_region(region_code)
        data = [{'codigo': c['codigo'], 'nombre': c['nombre']} for c in comunas]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

##########################################################
# CRUD GRUPOS Y USUARIOS
##########################################################  
class GrupoListView(PuedeGestionarUsuariosMixin, ListView):
    model = Group
    template_name = 'usuarios/grupo_list.html'
    context_object_name = 'grupos'
    permission_required = 'portal.gestionar_usuario'

class GrupoUpdateView(PuedeGestionarUsuariosMixin, UpdateView):
    model = Group
    template_name = 'usuarios/grupo_form.html'
    fields = ['name', 'permissions']
    success_url = reverse_lazy('grupo_list')
    permission_required = 'portal.gestionar_usuario'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar permisos solo de la app portal
        form.fields['permissions'].queryset = Permission.objects.filter(
            content_type__app_label='portal'
        )
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Grupo {form.instance.name} actualizado correctamente.')
        return super().form_valid(form)

class UsuarioGrupoUpdateView(PuedeGestionarUsuariosMixin, UpdateView):
    model = PerfilUsuario
    template_name = 'usuarios/usuario_grupo_form.html'
    fields = ['groups']
    success_url = reverse_lazy('usuario_list')
    permission_required = 'portal.gestionar_usuario'
    
    def form_valid(self, form):
        messages.success(self.request, f'Grupos del usuario {form.instance.username} actualizados correctamente.')
        return super().form_valid(form)

@login_required
def forzar_actualizacion_grupos(request):
    if not request.user.has_perm('portal.gestionar_usuario'):
        raise PermissionDenied
    
    # Importar la señal para ejecutarla manualmente
    from portal.models import crear_grupos_y_permisos
    crear_grupos_y_permisos(None)
    
    messages.success(request, 'Grupos y permisos actualizados correctamente.')
    return redirect('grupo_list')

#########################################################

#CRUD REGION
##########################################################
class RegionListView(PuedeGestionarRegionesMixin, ListView):
    model = Region
    template_name = 'inmuebles/region_list.html'
    context_object_name = 'regiones'

class RegionCreateView(PuedeGestionarRegionesMixin, CreateView):
    model = Region
    template_name = 'inmuebles/region_form.html'
    form_class = RegionForm
    success_url = reverse_lazy('region_list')

class RegionUpdateView(PuedeGestionarRegionesMixin, UpdateView):
    model = Region
    template_name = 'inmuebles/region_form.html'
    form_class = RegionForm
    success_url = reverse_lazy('region_list')

class RegionDeleteView(PuedeGestionarRegionesMixin, DeleteView):
    model = Region
    template_name = 'inmuebles/region_confirm_delete.html'
    success_url = reverse_lazy('region_list')

#########################################################

#CRUD COMUNA
##########################################################
class ComunaListView(PuedeGestionarComunasMixin, ListView):
    model = Comuna
    template_name = 'inmuebles/comuna_list.html'
    context_object_name = 'comunas'

class ComunaCreateView(PuedeGestionarComunasMixin, CreateView):
    model = Comuna
    template_name = 'inmuebles/comuna_form.html'
    form_class = ComunaForm
    success_url = reverse_lazy('comuna_list')

class ComunaUpdateView(PuedeGestionarComunasMixin, UpdateView):
    model = Comuna
    template_name = 'inmuebles/comuna_form.html'
    form_class = ComunaForm
    success_url = reverse_lazy('comuna_list')

class ComunaDeleteView(PuedeGestionarComunasMixin, DeleteView):
    model = Comuna
    template_name = 'inmuebles/comuna_confirm_delete.html'
    success_url = reverse_lazy('comuna_list')

#########################################################

#CRUD INMUEBLE
##########################################################
class InmueblesListView(PermisoRequeridoMixin, ListView):
    model = Inmueble
    template_name = 'web/home.html'
    context_object_name = 'inmuebles'
    
    def test_func(self):
        # Solo usuarios autenticados pueden ver inmuebles
        return self.request.user.is_authenticated

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todos los inmuebles
        if user.has_perm('portal.ver_todos_inmuebles') or user.tipo_usuario == 'ADMINISTRADOR':
            return queryset
        
        # Arrendadores ven solo sus inmuebles
        if user.has_perm('portal.gestionar_inmueble') or user.tipo_usuario == 'ARRENDADOR':
            return queryset.filter(propietario=user)
        
        # Arrendatarios ven solo inmuebles publicados
        return queryset.filter(esta_publicado=True) if hasattr(Inmueble, 'esta_publicado') else queryset.none()

class InmuebleCreateView(PuedeGestionarInmueblesMixin, CreateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')
    
    def form_valid(self, form):
        form.instance.propietario = self.request.user
        return super().form_valid(form)

class InmuebleUpdateView(PuedeGestionarInmueblesMixin, UpdateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Si no es administrador, solo puede editar sus propios inmuebles
        if not self.request.user.has_perm('portal.ver_todos_inmuebles'):
            return queryset.filter(propietario=self.request.user)
        return queryset

class InmuebleDeleteView(PuedeGestionarInmueblesMixin, DeleteView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_confirm_delete.html'
    success_url = reverse_lazy('inmueble_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Si no es administrador, solo puede eliminar sus propios inmuebles
        if not self.request.user.has_perm('portal.ver_todos_inmuebles'):
            return queryset.filter(propietario=self.request.user)
        return queryset

#########################################################
#CRUD SOLICITUD ARRIENDO
##########################################################
class SolicitudArriendoListView(PuedeGestionarSolicitudesMixin, ListView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_list.html'
    context_object_name = 'solicitudes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todas las solicitudes
        if user.has_perm('portal.ver_todos_inmuebles'):
            return queryset
        
        # Arrendadores ven solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'):
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios ven solo sus propias solicitudes
        return queryset.filter(arrendatario=user)

class SolicitudArriendoCreateView(LoginRequiredMixin, CreateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('perfil')
    
    def dispatch(self, request, *args, **kwargs):
        self.inmueble = get_object_or_404(Inmueble, pk=kwargs['inmueble_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        solicitud = form.save(commit=False)
        solicitud.inmueble = self.inmueble
        solicitud.arrendatario = self.request.user
        solicitud.save()
        messages.success(self.request, 'Solicitud de arriendo creada correctamente.')
        return redirect(self.success_url)

class SolicitudArriendoUpdateView(PuedeGestionarSolicitudesMixin, UpdateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('solicitud_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores pueden editar todas las solicitudes
        if user.has_perm('portal.ver_todos_inmuebles'):
            return queryset
        
        # Arrendadores pueden editar solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'):
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios pueden editar solo sus propias solicitudes
        return queryset.filter(arrendatario=user)

class SolicitudArriendoDeleteView(PuedeGestionarSolicitudesMixin, DeleteView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_confirm_delete.html'
    success_url = reverse_lazy('solicitud_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores pueden eliminar todas las solicitudes
        if user.has_perm('portal.ver_todos_inmuebles'):
            return queryset
        
        # Arrendadores pueden eliminar solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'):
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios pueden eliminar solo sus propias solicitudes
        return queryset.filter(arrendatario=user)
    
#########################################################

# CRUD PERFIL USUARIO
##########################################################

class PerfilUserUpdateView(UpdateView):
    model = PerfilUsuario
    template_name = 'usuarios/perfil_form.html'
    form_class = PerfilUsuarioForm
    success_url = reverse_lazy('solicitud_list')

@method_decorator(login_required, name='dispatch')
class PerfilView(UpdateView):
    template_name = 'usuarios/perfil.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        # Solicitadas por mí (si soy arrendatario)
        enviadas = (
            u.solicitudes_enviadas
            .select_related('inmueble')
            .order_by('-creado')
        )

        # Recibidas en mis inmuebles (si soy arrendador)
        recibidas = (
            SolicitudArriendo.objects
            .filter(inmueble__propietario=u)
            .select_related('inmueble', 'arrendatario')
            .order_by('-creado')
        )

        ctx.update({
            'enviadas': enviadas,
            'recibidas': recibidas,
        })
        return ctx


#login/logout/register
##########################################################

def register_view(request):
    if request.user.is_authenticated:  # Prevenir acceso si ya está autenticado
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

########################################################
# Login usando vistas basadas en clases
#########################################################
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        messages.success(self.request, 'Has iniciado sesión correctamente.')
        return reverse_lazy('home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error en el inicio de sesión. Verifica tus credenciales.')
        return super().form_invalid(form)

########################################################
# Logout usando vistas basadas en clases
#########################################################
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Acabas de cerrar sesión correctamente.')
        return super().dispatch(request, *args, **kwargs)
    
########################################################
# Vista para la página de inicio
#########################################################
# Esta vista mostrará las propiedades destacadas para todos los usuarios.
def home_view(request):
    inmuebles = Inmueble.objects.filter(esta_publicado=True)
    return render(request, 'web/home.html', {'inmuebles': inmuebles})
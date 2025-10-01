# backend/portal/views.py
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import (ListView, CreateView, UpdateView, DeleteView, DetailView)
from django.urls import reverse
from django.http import JsonResponse
import logging
from .forms import LoginForm, RegisterForm
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


class BasePermissionMixin(UserPassesTestMixin):
    """Mixin base simplificado para permisos"""
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        # Verificar permisos específicos
        permisos_requeridos = getattr(self, 'permisos_requeridos', [])
        if permisos_requeridos:
            return any(user.has_perm(permiso) for permiso in permisos_requeridos)
        
        # Verificar por tipo de usuario
        tipo_usuario_requerido = getattr(self, 'tipo_usuario_requerido', None)
        if tipo_usuario_requerido:
            return user.tipo_usuario == tipo_usuario_requerido
        
        return True
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "No tienes permisos para acceder a esta página.")
            return redirect('perfil')
        return redirect('login')

# Mixins simplificados
class ArrendadorMixin(BasePermissionMixin):
    tipo_usuario_requerido = 'ARRENDADOR'

class AdministradorMixin(BasePermissionMixin):
    tipo_usuario_requerido = 'ADMINISTRADOR'

class PuedeGestionarInmueblesMixin(BasePermissionMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.tipo_usuario in ['ARRENDADOR', 'ADMINISTRADOR'] or
            user.has_perm('portal.agregar_inmueble')
        )

logger = logging.getLogger(__name__)

@require_GET
@csrf_exempt
def cargar_comunas(request):
    """Vista para cargar comunas basadas en la región seleccionada"""
    region_code = request.GET.get('region', '').strip()
    
    logger.info(f"=== SOLICITUD CARGAR COMUNAS ===")
    logger.info(f"Parámetro región recibido: '{region_code}'")
    logger.info(f"Headers: {dict(request.headers)}")
    
    if not region_code:
        logger.warning("Código de región no proporcionado")
        return JsonResponse({'error': 'Código de región no proporcionado', 'comunas': []}, status=400)
    
    try:
        logger.info(f"Buscando comunas para región: {region_code}")
        comunas = ChileanLocationService.get_comunas_by_region(region_code)
        logger.info(f"Comunas encontradas: {len(comunas)}")
        
        # Log las primeras 3 comunas para debugging
        for i, comuna in enumerate(comunas[:3]):
            logger.info(f"Comuna {i+1}: {comuna}")
        
        if not comunas:
            logger.warning(f"No se encontraron comunas para la región {region_code}")
            return JsonResponse({
                'error': f'No se encontraron comunas para la región {region_code}',
                'comunas': []
            }, status=404)
        
        logger.info("Enviando respuesta con comunas")
        return JsonResponse(comunas, safe=False)
        
    except Exception as e:
        logger.error(f"Error crítico en cargar_comunas: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error interno del servidor: {str(e)}',
            'comunas': []
        }, status=500)

##########################################################
# CRUD GRUPOS Y USUARIOS
##########################################################  

# Nueva vista para listar usuarios
class UsuarioListView(PuedeGestionarUsuariosMixin, ListView):
    model = PerfilUsuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    permission_required = 'portal.gestionar_usuario'

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
        ).order_by('name') # Ordenar para mejor visualización
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Grupo {form.instance.name} actualizado correctamente.')
        return super().form_valid(form)

class UsuarioGrupoUpdateView(PuedeGestionarUsuariosMixin, UpdateView):
    model = PerfilUsuario
    template_name = 'usuarios/usuario_grupo_form.html'
    # Solo permitimos cambiar los grupos, no el tipo_usuario directamente aquí,
    # ya que tipo_usuario podría estar relacionado con la lógica de negocio
    # y los grupos son la forma de asignar permisos.
    fields = ['groups'] 
    success_url = reverse_lazy('usuario_list') # Redirigir a la lista de usuarios
    permission_required = 'portal.gestionar_usuario'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # El queryset de grupos ya debería estar bien por defecto
        # form.fields['groups'].queryset = Group.objects.all().order_by('name')
        return form

    def form_valid(self, form):
        messages.success(self.request, f'Grupos del usuario {form.instance.username} actualizados correctamente.')
        return super().form_valid(form)

@login_required
def forzar_actualizacion_grupos(request):
    if not request.user.has_perm('portal.gestionar_usuario'):
        raise PermissionDenied("No tienes permisos para forzar la actualización de grupos.")
    
    # Importar la señal para ejecutarla manualmente
    from portal.models import crear_grupos_y_permisos
    crear_grupos_y_permisos(None) # El 'sender' no es relevante aquí, se puede pasar None
    
    messages.success(request, 'Grupos y permisos actualizados correctamente.')
    return redirect('grupo_list')

#########################################################

#CRUD REGION
##########################################################

class RegionListView(PuedeGestionarRegionesMixin, ListView):
    model = Region
    template_name = 'inmuebles/region_list.html'
    context_object_name = 'regiones'
    # No es necesario definir permission_required en el ListView si ya usas el Mixin
    # El mixin PermisoRequeridoMixin ya maneja la lógica de test_func y handle_no_permission

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

class InmueblesListView(ListView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_list.html'
    context_object_name = 'inmuebles'
    paginate_by = 9
    
    def get_queryset(self):
        # Solo mostrar inmuebles publicados para usuarios normales
        queryset = Inmueble.objects.filter(esta_publicado=True).order_by('-creado')
        
        user = self.request.user
        # Administradores pueden ver todos los inmuebles
        if user.is_authenticated and (user.is_superuser or user.tipo_usuario == 'ADMINISTRADOR'):
            queryset = Inmueble.objects.all().order_by('-creado')
        
        logger.info(f"InmueblesListView - Mostrando {queryset.count()} inmuebles")
        return queryset

class InmuebleCreateView(PuedeGestionarInmueblesMixin, CreateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    
    def get_success_url(self):
        return reverse_lazy('perfil')
    
    def form_valid(self, form):
        try:
            # Asignar propietario automáticamente
            form.instance.propietario = self.request.user
            
            # Determinar estado de publicación
            puede_publicar = (
                self.request.user.has_perm('portal.publicar_inmueble') or 
                self.request.user.tipo_usuario == 'ADMINISTRADOR'
            )
            form.instance.esta_publicado = puede_publicar
            
            # Guardar nombres de ubicación
            self._guardar_ubicacion(form)
            
            response = super().form_valid(form)
            
            # Mensaje de éxito
            if puede_publicar:
                messages.success(self.request, 'INMUEBLE_CREADO_EXITOSAMENTE')
            else:
                messages.success(self.request, 'INMUEBLE_CREADO_PENDIENTE')
            
            return response
            
        except Exception as e:
            logger.error(f"Error al crear inmueble: {e}")
            messages.error(self.request, 'Error al crear el inmueble. Por favor intenta nuevamente.')
            return self.form_invalid(form)
    
    def _guardar_ubicacion(self, form):
        """Método auxiliar para guardar nombres de región y comuna"""
        region_codigo = form.cleaned_data.get('region_codigo')
        comuna_codigo = form.cleaned_data.get('comuna_codigo')
        
        if region_codigo:
            try:
                regiones = ChileanLocationService.get_regiones()
                region_nombre = next((r['nombre'] for r in regiones if r['codigo'] == region_codigo), '')
                form.instance.region_nombre = region_nombre
            except Exception as e:
                logger.error(f"Error obteniendo nombre de región: {e}")
        
        if comuna_codigo and region_codigo:
            try:
                comunas = ChileanLocationService.get_comunas_by_region(region_codigo)
                comuna_nombre = next((c['nombre'] for c in comunas if c['codigo'] == comuna_codigo), '')
                form.instance.comuna_nombre = comuna_nombre
            except Exception as e:
                logger.error(f"Error obteniendo nombre de comuna: {e}")
    
    def form_invalid(self, form):
        logger.error(f"Formulario inválido: {form.errors}")
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)

class InmuebleUpdateView(PuedeGestionarInmueblesMixin, UpdateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Si no es administrador, solo puede editar sus propios inmuebles
        if not (user.is_superuser or user.has_perm('portal.ver_todos_inmuebles')): # 'is_superuser' para cubrir el admin por defecto
            queryset = queryset.filter(propietario=user)
        return queryset

    def form_valid(self, form):
        # Permiso para publicar/despublicar
        if 'esta_publicado' in form.cleaned_data and not self.request.user.has_perm('portal.publicar_inmueble'):
            # Si el usuario no tiene permiso para publicar, no permitimos que cambie el campo
            del form.cleaned_data['esta_publicado'] # Eliminar el campo del formulario para que no se guarde
            messages.warning(self.request, "No tienes permiso para cambiar el estado de publicación del inmueble.")
        return super().form_valid(form)


class InmuebleDeleteView(PuedeGestionarInmueblesMixin, DeleteView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_confirm_delete.html'
    success_url = reverse_lazy('inmueble_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Si no es administrador, solo puede eliminar sus propios inmuebles
        if not (user.is_superuser or user.has_perm('portal.ver_todos_inmuebles')):
            queryset = queryset.filter(propietario=user)
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
        if user.is_superuser or user.has_perm('portal.ver_todos_inmuebles'): # 'ver_todos_inmuebles' como proxy para admin
            return queryset
        
        # Arrendadores ven solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'): # 'gestionar_inmueble' como proxy para arrendador
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios ven solo sus propias solicitudes
        return queryset.filter(arrendatario=user)

class SolicitudArriendoCreateView(LoginRequiredMixin, CreateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    # Cambiamos success_url para redirigir a la vista de detalle del inmueble o al perfil
    # La actual (perfil) está bien para un arrendatario que ha hecho una solicitud
    success_url = reverse_lazy('perfil') 
    
    def dispatch(self, request, *args, **kwargs):
        # Es crucial que el inmueble_pk llegue en los kwargs de la URL
        self.inmueble = get_object_or_404(Inmueble, pk=kwargs['inmueble_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inmueble'] = self.inmueble # Pasar el inmueble al contexto
        return context

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
        if user.is_superuser or user.has_perm('portal.ver_todos_inmuebles'):
            return queryset
        
        # Arrendadores pueden editar solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'):
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios pueden editar solo sus propias solicitudes
        # Aquí podrían editar solo el mensaje o cancelar, no el estado
        return queryset.filter(arrendatario=user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Si el usuario no tiene permiso para aprobar/rechazar,
        # hacemos el campo 'estado' de solo lectura.
        if not (user.is_superuser or user.has_perm('portal.aprobar_solicitud')):
            form.fields['estado'].widget.attrs['disabled'] = 'disabled'
            form.fields['estado'].required = False # Opcional: para evitar errores si no se envía
        return form

    def form_valid(self, form):
        # Si el campo estado fue deshabilitado, necesitamos recuperarlo de la instancia original
        if 'estado' not in form.cleaned_data:
            form.instance.estado = self.get_object().estado
        
        messages.success(self.request, 'Solicitud de arriendo actualizada correctamente.')
        return super().form_valid(form)


class SolicitudArriendoDeleteView(PuedeGestionarSolicitudesMixin, DeleteView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_confirm_delete.html'
    success_url = reverse_lazy('solicitud_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores pueden eliminar todas las solicitudes
        if user.is_superuser or user.has_perm('portal.ver_todos_inmuebles'):
            return queryset
        
        # Arrendadores pueden eliminar solicitudes de sus inmuebles
        if user.has_perm('portal.gestionar_inmueble'):
            return queryset.filter(inmueble__propietario=user)
        
        # Arrendatarios pueden eliminar solo sus propias solicitudes
        return queryset.filter(arrendatario=user)
    
#########################################################

# CRUD PERFIL USUARIO
##########################################################
class PerfilUserUpdateView(LoginRequiredMixin, UpdateView): # Añadir LoginRequiredMixin
    model = PerfilUsuario
    template_name = 'usuarios/perfil_form.html'
    form_class = PerfilUsuarioForm
    success_url = reverse_lazy('perfil') # Redirigir al perfil después de actualizar
    
    def get_object(self, queryset=None):
        # El usuario solo puede editar su propio perfil
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ocultar o deshabilitar campos sensibles si no se deben editar por el usuario
        # Por ejemplo, el tipo_usuario no debería ser editable por el usuario normal
        # El password se maneja de forma segura por defecto con AbstractUser
        if 'tipo_usuario' in form.fields:
            form.fields['tipo_usuario'].widget.attrs['readonly'] = 'readonly'
            form.fields['tipo_usuario'].widget.attrs['disabled'] = 'disabled'
            form.fields['tipo_usuario'].required = False # No es requerido si está deshabilitado
        if 'password' in form.fields: # Normalmente se usa un flujo de cambio de contraseña separado
            del form.fields['password'] # Quitar el campo de password de la edición de perfil
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Tu perfil ha sido actualizado correctamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PerfilView(DetailView):
    model = PerfilUsuario
    template_name = 'usuarios/perfil.html'
    context_object_name = 'perfil'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            # Mis inmuebles (si soy arrendador o administrador)
            mis_inmuebles = Inmueble.objects.filter(propietario=user).order_by('-creado')
            
            # Solicitadas por mí (si soy arrendatario)
            enviadas = SolicitudArriendo.objects.filter(
                arrendatario=user
            ).select_related('inmueble').order_by('-creado')

            # Recibidas en mis inmuebles (si soy arrendador)
            recibidas = SolicitudArriendo.objects.filter(
                inmueble__propietario=user
            ).select_related('inmueble', 'arrendatario').order_by('-creado')

            context.update({
                'enviadas': enviadas,
                'recibidas': recibidas,
                'mis_inmuebles': mis_inmuebles,
                'total_inmuebles': mis_inmuebles.count(),
                'total_solicitudes_enviadas': enviadas.count(),
                'total_solicitudes_recibidas': recibidas.count(),
            })
            
        except Exception as e:
            logger.error(f"Error en PerfilView: {e}")
            # En caso de error, establecer valores por defecto
            context.update({
                'enviadas': [],
                'recibidas': [],
                'mis_inmuebles': [],
                'total_inmuebles': 0,
                'total_solicitudes_enviadas': 0,
                'total_solicitudes_recibidas': 0,
            })

        return context

#login/logout/register
##########################################################

@csrf_protect # Asegurar protección CSRF
def register_view(request):
    if request.user.is_authenticated:  # Prevenir acceso si ya está autenticado
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- NUEVA LÓGICA: Asignar usuario a grupo al registrarse ---
            # Esto duplica un poco la lógica de post_migrate, pero asegura
            # que el usuario tenga su grupo inmediatamente después del registro.
            # Puedes llamar a la función crear_grupos_y_permisos aquí para reasignar todo
            # O simplemente asignar al nuevo usuario:
            try:
                if user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR:
                    grupo = Group.objects.get(name='Administradores')
                elif user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDADOR:
                    grupo = Group.objects.get(name='Arrendadores')
                elif user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDATARIO:
                    grupo = Group.objects.get(name='Arrendatarios')
                else:
                    grupo = None # Manejar caso por defecto si es necesario
                
                if grupo:
                    user.groups.add(grupo)
                    user.save()
            except Group.DoesNotExist:
                messages.error(request, 'Error: El grupo para tu tipo de usuario no existe. Contacta al administrador.')
            # --- FIN NUEVA LÓGICA ---
            
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
    """Vista para la página de inicio que muestra propiedades publicadas"""
    try:
        # Mostrar inmuebles publicados, ordenados por los más recientes
        inmuebles = Inmueble.objects.filter(esta_publicado=True).order_by('-creado')[:8]
        
        # Obtener estadísticas para mostrar en el home
        total_inmuebles = Inmueble.objects.filter(esta_publicado=True).count()
        total_arrendadores = PerfilUsuario.objects.filter(
            tipo_usuario=PerfilUsuario.TipoUsuario.ARRENDADOR
        ).count()
        
        logger.info(f"Home - Mostrando {inmuebles.count()} inmuebles publicados")
        
        context = {
            'inmuebles': inmuebles,
            'total_inmuebles': total_inmuebles,
            'total_arrendadores': total_arrendadores,
        }
        return render(request, 'web/home.html', context)
        
    except Exception as e:
        logger.error(f"Error en home_view: {e}")
        return render(request, 'web/home.html', {'inmuebles': []})
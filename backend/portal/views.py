# backend/portal/views.py

from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
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
    PerfilUsuario,
    ImagenInmueble,
)

from .forms import (
    RegionForm,
    ComunaForm,
    InmuebleForm,
    SolicitudArriendoForm,
    PerfilUsuarioForm,
    ImagenInmuebleForm,
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

class InmueblesListView(PermisoRequeridoMixin, ListView):
    model = Inmueble
    template_name = 'web/home.html' # Ojo: esta vista se usa para el home, pero su nombre es InmueblesListView.
                                   # Podría ser confuso.
    context_object_name = 'inmuebles'
    
    def test_func(self):
        # Todos los usuarios autenticados y no autenticados pueden ver inmuebles publicados en el home.
        # Si esta vista es específicamente para listar "todos" los inmuebles gestionables,
        # entonces el permiso 'portal.ver_todos_inmuebles' o 'portal.gestionar_inmueble' debería aplicarse.
        # Para el home, creo que es mejor que sea accesible por todos.
        return True # Permitir a todos ver el home. La lógica de queryset filtra lo que ven.

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si la vista es la del HOME, queremos que todos vean los publicados
        if self.request.resolver_match.url_name == 'home':
             return queryset.filter(esta_publicado=True)

        # Si esta vista se usa para una gestión de inmuebles (ej: '/listar_inmuebles/'), 
        # entonces aplicamos la lógica de permisos.
        if user.is_authenticated:
            # Administradores ven todos los inmuebles
            if user.has_perm('portal.ver_todos_inmuebles') or user.tipo_usuario == 'ADMINISTRADOR':
                return queryset
            
            # Arrendadores ven solo sus inmuebles
            if user.has_perm('portal.gestionar_inmueble') or user.tipo_usuario == 'ARRENDADOR':
                return queryset.filter(propietario=user)
            
            # Arrendatarios, si llegan aquí, solo verían publicados (aunque ya se filtró en el home)
            return queryset.filter(esta_publicado=True) 
        
        # Usuarios no autenticados solo ven publicados (si 'esta_publicado' existe)
        return queryset.filter(esta_publicado=True) if hasattr(Inmueble, 'esta_publicado') else queryset.none()


class InmuebleCreateView(PuedeGestionarInmueblesMixin, CreateView):
    # Solo arrendadores pueden crear inmuebles
    model = Inmueble
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')
    
    def form_valid(self, form):
        # Si es arrendador, se asigna como propietario
        if self.request.user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDADOR:
            form.instance.propietario = self.request.user
        # Los administradores pueden elegir el propietario en el formulario
        return super().form_valid(form)

class InmuebleUpdateView(PuedeGestionarInmueblesMixin, UpdateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores pueden editar todos los inmuebles
        if user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR:
            return queryset
        
        # Arrendadores solo pueden editar sus inmuebles
        return queryset.filter(propietario=user)

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

##################################################################
# IMAGEN INMUEBLE
##################################################################

from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

class ImagenInmuebleCreateView(EsArrendadorMixin, CreateView):
    model = ImagenInmueble
    form_class = ImagenInmuebleForm
    template_name = 'inmuebles/imagen_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.inmueble = get_object_or_404(Inmueble, pk=kwargs['inmueble_pk'])
        # Verificar que el usuario es el propietario del inmueble
        if self.inmueble.propietario != request.user:
            raise PermissionDenied("No tienes permiso para agregar imágenes a este inmueble")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inmueble'] = self.inmueble
        return context
    
    def form_valid(self, form):
        form.instance.inmueble = self.inmueble
        messages.success(self.request, 'Imagen agregada correctamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('actualizar_inmueble', kwargs={'pk': self.inmueble.pk})

class ImagenInmuebleDeleteView(EsArrendadorMixin, DeleteView):
    model = ImagenInmueble
    template_name = 'inmuebles/imagen_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que el usuario es el propietario del inmueble
        imagen = self.get_object()
        if imagen.inmueble.propietario != request.user:
            raise PermissionDenied("No tienes permiso para eliminar esta imagen")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Imagen eliminada correctamente.')
        return reverse_lazy('actualizar_inmueble', kwargs={'pk': self.object.inmueble.pk})

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
class PerfilView(UpdateView): # Aquí debería ser DetailView o una View combinada, no UpdateView si no editas
    model = PerfilUsuario # Definir el modelo para la DetailView
    template_name = 'usuarios/perfil.html'
    context_object_name = 'perfil' # Nombre del objeto en el contexto

    def get_object(self, queryset=None):
        # Asegurarse de que solo se vea el perfil del usuario logueado
        return self.request.user

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
    inmuebles = Inmueble.objects.filter(esta_publicado=True)
    return render(request, 'web/home.html', {'inmuebles': inmuebles})
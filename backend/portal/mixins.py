from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

class PermisoRequeridoMixin(UserPassesTestMixin):
    """Mixin base para verificar permisos"""
    
    def test_func(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return False
        
        # Verificar permisos específicos
        permisos_requeridos = getattr(self, 'permisos_requeridos', [])
        if permisos_requeridos:
            if not any(user.has_perm(permiso) for permiso in permisos_requeridos):
                return False
        
        # Verificar grupos
        grupos_requeridos = getattr(self, 'grupos_requeridos', [])
        if grupos_requeridos:
            if not user.groups.filter(name__in=grupos_requeridos).exists():
                return False
        
        return True
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("No tienes permisos para acceder a esta página")
        return redirect('login')

# Mixins específicos actualizados
class PuedeGestionarInmueblesMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.agregar_inmueble', 'portal.ver_todos_inmuebles']
    grupos_requeridos = ['Arrendadores', 'Administradores']

class PuedeVerTodosInmueblesMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.ver_todos_inmuebles']
    grupos_requeridos = ['Administradores']

class PuedeGestionarSolicitudesMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.gestionar_solicitud']

class PuedeAprobarSolicitudesMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.aprobar_solicitud']

class PuedeGestionarUsuariosMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.gestionar_usuario']
    grupos_requeridos = ['Administradores']

class PuedeGestionarRegionesMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.gestionar_region']
    grupos_requeridos = ['Administradores']

class PuedeGestionarComunasMixin(PermisoRequeridoMixin):
    permisos_requeridos = ['portal.gestionar_comuna']
    grupos_requeridos = ['Administradores']

# Mixins por tipo de usuario (basados en el campo tipo_usuario del modelo)
class EsAdministradorMixin(PermisoRequeridoMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.tipo_usuario == 'ADMINISTRADOR'

class EsArrendadorMixin(PermisoRequeridoMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.tipo_usuario == 'ARRENDADOR'

class EsArrendatarioMixin(PermisoRequeridoMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.tipo_usuario == 'ARRENDATARIO'

# Mixins por grupo (alternativa)
class GrupoAdministradoresMixin(PermisoRequeridoMixin):
    grupos_requeridos = ['Administradores']

class GrupoArrendadoresMixin(PermisoRequeridoMixin):
    grupos_requeridos = ['Arrendadores']

class GrupoArrendatariosMixin(PermisoRequeridoMixin):
    grupos_requeridos = ['Arrendatarios']
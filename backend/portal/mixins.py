# backend/portal/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

class PermisoRequeridoMixin(UserPassesTestMixin):
    """Mixin para verificar permisos específicos"""
    permiso_requerido = None
    grupo_requerido = None
    tipo_usuario_requerido = None
    
    def test_func(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return False
        
        # Verificar permiso específico
        if self.permiso_requerido and not user.has_perm(self.permiso_requerido):
            return False
        
        # Verificar grupo
        if self.grupo_requerido and not user.groups.filter(name=self.grupo_requerido).exists():
            return False
        
        # Verificar tipo de usuario
        if self.tipo_usuario_requerido and user.tipo_usuario != self.tipo_usuario_requerido:
            return False
        
        return True
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("No tienes permisos para acceder a esta página")
        return redirect('login')

# Mixins específicos para permisos comunes
class PuedeGestionarInmueblesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_inmueble'

class PuedeVerTodosInmueblesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.ver_todos_inmuebles'

class PuedeGestionarSolicitudesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_solicitud'

class PuedeAprobarSolicitudesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.aprobar_solicitud'

class PuedeGestionarUsuariosMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_usuario'

class PuedeVerTodosUsuariosMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.ver_todos_usuarios'

class PuedeGestionarRegionesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_region'

class PuedeGestionarComunasMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_comuna'

# Mixins por tipo de usuario
class EsAdministradorMixin(PermisoRequeridoMixin):
    tipo_usuario_requerido = 'ADMINISTRADOR'

class EsArrendadorMixin(PermisoRequeridoMixin):
    tipo_usuario_requerido = 'ARRENDADOR'

class EsArrendatarioMixin(PermisoRequeridoMixin):
    tipo_usuario_requerido = 'ARRENDATARIO'

# Mixins por grupo
class GrupoAdministradoresMixin(PermisoRequeridoMixin):
    grupo_requerido = 'Administradores'

class GrupoArrendadoresMixin(PermisoRequeridoMixin):
    grupo_requerido = 'Arrendadores'

class GrupoArrendatariosMixin(PermisoRequeridoMixin):
    grupo_requerido = 'Arrendatarios'
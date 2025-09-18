# backend/portal/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import PerfilUsuario

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
class PuedeGestionarInmueblesMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Administradores y arrendadores pueden gestionar inmuebles
        return (user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR or 
                user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDADOR)

class PuedeVerTodosInmueblesMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Administradores pueden ver todos los inmuebles
        return user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR

class PuedeGestionarSolicitudesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_solicitud'

class PuedeAprobarSolicitudesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.aprobar_solicitud'

class PuedeGestionarUsuariosMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Solo administradores pueden gestionar usuarios
        return user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR

class PuedeVerTodosUsuariosMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.ver_todos_usuarios'

class PuedeGestionarRegionesMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_region'

class PuedeGestionarComunasMixin(PermisoRequeridoMixin):
    permiso_requerido = 'portal.gestionar_comuna'

# Mixins por tipo de usuario
class EsAdministradorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo_usuario == PerfilUsuario.TipoUsuario.ADMINISTRADOR

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

class EsArrendadorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDADOR

class EsArrendatarioMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo_usuario == PerfilUsuario.TipoUsuario.ARRENDATARIO
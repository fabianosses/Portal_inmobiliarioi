# backend/portal/context_processors.py
from .models import Inmueble

def inmuebles_pendientes_count(request):
    if request.user.is_authenticated and (request.user.tipo_usuario == 'ADMINISTRADOR' or request.user.is_superuser):
        count = Inmueble.objects.filter(esta_publicado=False).count()
        return {'inmuebles_pendientes_count': count}
    return {'inmuebles_pendientes_count': 0}
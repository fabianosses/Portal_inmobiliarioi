# backend/portal/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .services import ChileanLocationService

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

def HomeInmuebleListView (request):
    return render(request, 'web/home.html')

#########################################################

#CRUD REGION
##########################################################
class RegionListView(ListView):
    model = Region
    template_name = 'inmuebles/region_list.html'
    context_object_name = 'regiones'

class RegionCreateView(CreateView):
    model = Region
    template_name = 'inmuebles/region_form.html'
    form_class = RegionForm
    success_url = reverse_lazy('region_list')   

class RegionUpdateView(UpdateView):
    model = Region
    template_name = 'inmuebles/region_form.html'
    form_class = RegionForm
    success_url = reverse_lazy('region_list')   

class RegionDeleteView(DeleteView):
    model = Region
    template_name = 'inmuebles/region_confirm_delete.html'
    success_url = reverse_lazy('region_list')

#########################################################

#CRUD COMUNA
##########################################################

class ComunaListView(ListView):
    model = Comuna
    template_name = 'inmuebles/comuna_list.html'
    context_object_name = 'comunas'

class ComunaCreateView(CreateView):
    model = Comuna
    template_name = 'inmuebles/comuna_form.html'
    form_class = ComunaForm
    success_url = reverse_lazy('comuna_list')

class ComunaUpdateView(UpdateView):
    model = Comuna
    template_name = 'inmuebles/comuna_form.html'
    form_class = ComunaForm
    success_url = reverse_lazy('comuna_list')

class ComunaDeleteView(DeleteView):
    model = Comuna
    template_name = 'inmuebles/comuna_confirm_delete.html'
    success_url = reverse_lazy('comuna_list')


#########################################################

#CRUD INMUEBLE
##########################################################

class InmueblesListView(ListView):
    model = Inmueble
    template_name = 'web/home.html'
    context_object_name = 'inmuebles'

    def get_queryset(self):
        queryset = super().get_queryset()
        comuna_codigo = self.request.GET.get('comuna')
        if comuna_codigo:
            queryset = queryset.filter(comuna_codigo=comuna_codigo)
        return queryset

class InmuebleCreateView(CreateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')

class InmuebleUpdateView(UpdateView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_form.html'
    form_class = InmuebleForm
    success_url = reverse_lazy('inmueble_list')

class InmuebleDeleteView(DeleteView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_confirm_delete.html'
    success_url = reverse_lazy('inmueble_list')


#########################################################
#CRUD SOLICITUD ARRIENDO
##########################################################

class SolicitudArriendoListView(ListView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_list.html'
    context_object_name = 'solicitudes'

class SolicitudArriendoCreateView(CreateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('perfil') # o donde quieras

    def dispatch(self, request, *args, **kwargs):
        # Cargamos el inmueble una vez para reutilizarlo
        self.inmueble = get_object_or_404(Inmueble, pk=kwargs['inmueble_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inmueble'] = self.inmueble
        return ctx
    
    def form_valid(self, form):
        solicitud = form.save(commit=False)
        solicitud.inmueble = self.inmueble
        solicitud.arrendatario = self.request.user
        solicitud.save()
        messages.success(self.request, 'Solicitud de arriendo creada correctamente.')
        return redirect(self.success_url)

class SolicitudArriendoUpdateView(UpdateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('solicitud_list')

class SolicitudArriendoDeleteView(DeleteView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_confirm_delete.html'
    success_url = reverse_lazy('solicitud_list')    
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
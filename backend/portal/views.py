from django.shortcuts import render
from django.urls import reverse_lazy

from .models import (
    Region,
    Comuna,
    Inmueble,
    SolicitudArriendo,
)

from .form import (
    RegionForm,
    ComunaForm,
    InmuebleForm,
    SolicitudArriendoForm
)

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)   

# Create your views here.
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

class InmuebleListView(ListView):
    model = Inmueble
    template_name = 'inmuebles/inmueble_list.html'
    context_object_name = 'inmuebles'

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
    context_object_name = 'solicitudesarriendo'

class SolicitudArriendoCreateView(CreateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('solicitudarriendo_list')

class SolicitudArriendoUpdateView(UpdateView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_form.html'
    form_class = SolicitudArriendoForm
    success_url = reverse_lazy('solicitudarriendo_list')

class SolicitudArriendoDeleteView(DeleteView):
    model = SolicitudArriendo
    template_name = 'inmuebles/solicitudarriendo_confirm_delete.html'
    success_url = reverse_lazy('solicitudarriendo_list')    
#########################################################
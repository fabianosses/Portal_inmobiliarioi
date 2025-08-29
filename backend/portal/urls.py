from django.urls import path
from .views import *


urlpatterns = [
    #path('inmuebles/', InmuebleListCreateView.as_view(), name='inmueble-list-create'),
    path('home/', home, name='home'),
    path('about/', about, name='about'),
]

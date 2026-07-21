# pqrs/urls.py
from django.urls import path
from . import views

app_name = 'pqrs'

urlpatterns = [
    path('', views.formulario_pqrs, name='formulario_pqrs'),
    path('exito/', views.pqrs_exito, name='pqrs_exito'),
]
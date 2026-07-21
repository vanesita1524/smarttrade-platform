from django.urls import path
from . import views

urlpatterns = [
    path("chat/panel-asesores/", views.panel_asesores, name="panel_asesores"),
    path('historial/', views.historial_ajax, name='historial_ajax'),
    path('room/', views.room, name='room'),
    path('', views.index, name='index'),
    ]

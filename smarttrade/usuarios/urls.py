from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home, name="home"),
    path('index/', views.index_view, name='index'),
    path("planes/", views.planes_view, name="planes"),
    path('registro/', views.registro, name='registro'),
    path("pqrs/", views.pqrs_view, name="pqrs"),
    path("reportes/", views.reportes_view, name="reportes"),
    path("perfil/", views.perfil_view, name="perfil"),
    path("cambiar-plan/", views.cambiar_plan, name="cambiar_plan"),

    # ✅ Nueva ruta
    path("cambiar-correo/", views.cambiar_correo, name="cambiar_correo"),
    # Rutas para restablecer contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
]
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from functools import wraps
from django.contrib.auth.models import User
from .models import Conversacion, MensajeAsesor

# --- Decoradores ---
def oro_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            plan = request.user.perfil.plan
        except:
            return HttpResponseForbidden("No tienes acceso")
        if plan.nombre.lower() != "oro":
            return HttpResponseForbidden("Solo usuarios con plan Oro pueden acceder")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def asesores_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name="asesores").exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Solo asesores pueden acceder")
    return _wrapped_view


# --- Vistas ---
@login_required
def index(request):
    return render(request, 'chat/index.html')


@login_required
@oro_required
def room(request):
    # Determinar el asesor asignado a este usuario (si existe).
    usuario = request.user

    conversacion = Conversacion.objects.filter(usuario=usuario).order_by('-creada').first()
    if conversacion:
        asesor = conversacion.asesor
    else:
        # Si no hay una conversación asignada, seleccionar el primer asesor disponible
        asesor = User.objects.filter(groups__name='asesores').first()

    if asesor is None:
        # No hay asesores registrados: denegar acceso
        return HttpResponseForbidden("No hay asesores disponibles")

    asesor_id = asesor.id
    # Construir room_name en el mismo formato que usa el panel de asesores
    room_name = f"user_{usuario.id}_asesor_{asesor_id}"

    # Obtener historial de mensajes
    conversacion_obj, _ = Conversacion.objects.get_or_create(usuario=usuario, asesor=asesor)
    mensajes = MensajeAsesor.objects.filter(conversacion=conversacion_obj).order_by('fecha')

    historial = [
        {"username": m.remitente.username, "mensaje": m.mensaje, "fecha": m.fecha.strftime('%d/%m/%Y %H:%M')}
        for m in mensajes
    ]

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'asesor_id': asesor_id,
        'historial': historial,
    })


@asesores_required
def panel_asesores(request):
    # Mostrar lista de usuarios con plan Oro
    usuarios_oro = User.objects.filter(perfil__plan__nombre__iexact="oro")

    # Si se seleccionó un usuario, cargar historial
    usuario_id = request.GET.get('usuario_id')
    historial = []
    chat_user = None
    if usuario_id:
        try:
            chat_user = User.objects.get(id=usuario_id)
            asesor = request.user
            conversacion_obj, _ = Conversacion.objects.get_or_create(usuario=chat_user, asesor=asesor)
            mensajes = MensajeAsesor.objects.filter(conversacion=conversacion_obj).order_by('fecha')
            historial = [
                {"username": m.remitente.username, "mensaje": m.mensaje, "fecha": m.fecha.strftime('%d/%m/%Y %H:%M')}
                for m in mensajes
            ]
        except User.DoesNotExist:
            pass

    return render(request, "chat/panel_asesores.html", {
        "usuarios_oro": usuarios_oro,
        "historial": historial,
        "chat_user": chat_user,
    })


@asesores_required
def historial_ajax(request):
    """Endpoint AJAX que devuelve el historial de conversación entre el asesor autenticado y el usuario indicado.

    Parámetros GET: usuario_id
    Respuesta JSON: { historial: [ {username, mensaje, fecha}, ... ], usuario: {id, username} }
    """
    usuario_id = request.GET.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'usuario_id requerido'}, status=400)
    try:
        usuario = User.objects.get(id=int(usuario_id))
    except (User.DoesNotExist, ValueError):
        return JsonResponse({'error': 'usuario no encontrado'}, status=404)

    asesor = request.user
    conversacion_obj, _ = Conversacion.objects.get_or_create(usuario=usuario, asesor=asesor)
    mensajes = MensajeAsesor.objects.filter(conversacion=conversacion_obj).order_by('fecha')
    historial = [
        {"username": m.remitente.username, "mensaje": m.mensaje, "fecha": m.fecha.strftime('%d/%m/%Y %H:%M')}
        for m in mensajes
    ]

    return JsonResponse({'historial': historial, 'usuario': {'id': usuario.id, 'username': usuario.username}})

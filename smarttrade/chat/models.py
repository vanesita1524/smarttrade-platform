from django.db import models
from django.contrib.auth.models import User

class Conversacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversaciones")
    asesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="asignaciones")
    creada = models.DateTimeField(auto_now_add=True)

class MensajeAsesor(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name="mensajes")
    remitente = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)


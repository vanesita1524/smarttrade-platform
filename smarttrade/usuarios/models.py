from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Plan(models.Model):
    nombre = models.CharField(max_length=20)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    beneficios = models.TextField()  # aquí puedes ponerlos separados por comas o luego hacer otra tabla
    
    def __str__(self):
        return self.nombre
    
class Perfil(models.Model):
    PLANES = [
        ('Básico', 'Básico'),
        ('Premium', 'Premium'),
        ('Oro', 'Oro'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class PQRS(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pqrs')
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    respuesta = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"PQRS de {self.nombre} - {self.estado}"
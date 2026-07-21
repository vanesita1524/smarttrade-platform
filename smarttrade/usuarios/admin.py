from django.contrib import admin
from .models import Plan, PQRS

# Register your models here.
admin.site.register(Plan)

@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('nombre', 'correo', 'mensaje', 'respuesta')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)
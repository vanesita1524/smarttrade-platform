from django.contrib import admin
from .models import Conversacion, MensajeAsesor

class MensajeAsesorInline(admin.TabularInline):
    model = MensajeAsesor
    extra = 0
    readonly_fields = ('fecha',)
    fields = ('remitente', 'mensaje', 'fecha')
    ordering = ('fecha',)

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'asesor', 'creada', 'mensajes_count')
    list_filter = ('asesor', 'creada')
    search_fields = ('usuario__username', 'asesor__username')
    date_hierarchy = 'creada'
    inlines = [MensajeAsesorInline]

    def mensajes_count(self, obj):
        return obj.mensajes.count()
    mensajes_count.short_description = 'Número de mensajes'

@admin.register(MensajeAsesor)
class MensajeAsesorAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_usuario', 'get_asesor', 'remitente', 'mensaje_corto', 'fecha')
    list_filter = ('fecha', 'remitente', 'conversacion__asesor')
    search_fields = ('mensaje', 'remitente__username')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'

    def get_usuario(self, obj):
        return obj.conversacion.usuario.username
    get_usuario.short_description = 'Usuario'
    get_usuario.admin_order_field = 'conversacion__usuario__username'

    def get_asesor(self, obj):
        return obj.conversacion.asesor.username
    get_asesor.short_description = 'Asesor'
    get_asesor.admin_order_field = 'conversacion__asesor__username'

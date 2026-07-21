import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatAsesorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ Conectado a sala: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        user = self.scope["user"]
        username = user.username if user.is_authenticated else "Anon"

        # Guardar el mensaje en la base de datos
        await self._save_message(user, message)

        print(f"💬 {username} -> {self.room_group_name}: {message}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    @sync_to_async
    def _save_message(self, remitente, mensaje):
        from django.contrib.auth.models import User
        from .models import Conversacion, MensajeAsesor
        # room_name: user_{usuario_id}_asesor_{asesor_id}
        try:
            parts = self.room_name.split('_')
            usuario_id = int(parts[1])
            asesor_id = int(parts[3])
        except Exception:
            return
        try:
            usuario = User.objects.get(id=usuario_id)
            asesor = User.objects.get(id=asesor_id)
        except User.DoesNotExist:
            return
        conversacion, _ = Conversacion.objects.get_or_create(usuario=usuario, asesor=asesor)
        MensajeAsesor.objects.create(conversacion=conversacion, remitente=remitente, mensaje=mensaje)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"]
        }))

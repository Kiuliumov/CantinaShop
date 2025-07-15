import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.user = user

        if user.is_staff or user.is_superuser:
            self.recipient_user_id = self.scope['url_route']['kwargs'].get('user_id')
            if not self.recipient_user_id:
                await self.close()
                return
            self.room_group_name = f'chat_{self.recipient_user_id}'
        else:
            self.room_group_name = f'chat_{user.id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        sender = self.user

        # Determine recipient for message:
        if sender.is_staff or sender.is_superuser:
            # Admin sends message to recipient user id from URL
            recipient = await self.get_user(self.recipient_user_id)
            if not recipient:
                return
        else:
            recipient = await self.get_admin_user()
            if not recipient:
                return

        chat_message = await self.save_message(sender, recipient, message)

        await self.channel_layer.group_send(
            f'chat_{recipient.id}',
            {
                'type': 'chat_message',
                'message': message,
                'username': sender.username,
                'avatar_url': chat_message.avatar_url,
                'timestamp': chat_message.timestamp.isoformat(),
                'sender_id': sender.id,
            }
        )

        if sender.id != recipient.id:
            await self.channel_layer.group_send(
                f'chat_{sender.id}',
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': sender.username,
                    'avatar_url': chat_message.avatar_url,
                    'timestamp': chat_message.timestamp.isoformat(),
                    'sender_id': sender.id,
                }
            )

    async def chat_message(self, event):
        # Send message event to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url'],
            'timestamp': event['timestamp'],
            'sender_id': event['sender_id'],
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_admin_user(self):
        return User.objects.filter(is_staff=True).first()

    @database_sync_to_async
    def save_message(self, sender, recipient, message):
        from .models import ChatMessage
        return ChatMessage.objects.create(sender=sender, recipient=recipient, message=message)

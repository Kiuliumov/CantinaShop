import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q


class BaseChatConsumer(AsyncWebsocketConsumer):
    is_from_admin = False

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
        if hasattr(self, 'room_group_name') and self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        sender = self.user

        if sender.is_staff or sender.is_superuser:
            recipient = await self.get_user(self.recipient_user_id)
            if not recipient:
                return
        else:
            recipient = await self.get_admin_user()
            if not recipient:
                return

        chat_message = await self.save_message(sender, recipient, message, self.is_from_admin)

        avatar_url = await self.get_avatar_url(chat_message)

        payload = {
            'type': 'chat_message',
            'message': message,
            'username': sender.username,
            'avatar_url': avatar_url,
            'timestamp': chat_message.timestamp.isoformat(),
            'sender_id': sender.id,
            'from_admin': self.is_from_admin,
        }

        await self.channel_layer.group_send(f'chat_{recipient.id}', payload)

        if sender.id != recipient.id:
            await self.channel_layer.group_send(f'chat_{sender.id}', payload)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url'],
            'timestamp': event['timestamp'],
            'sender_id': event['sender_id'],
            'from_admin': event.get('from_admin', False),
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_admin_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).first()

    @database_sync_to_async
    def save_message(self, sender, recipient, message, is_from_admin):
        from .models import ChatMessage
        return ChatMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message=message,
            is_from_admin=is_from_admin,
        )

    @database_sync_to_async
    def get_avatar_url(self, chat_message):
        return chat_message.avatar_url


class UserConsumer(BaseChatConsumer):
    is_from_admin = False


class AdminConsumer(BaseChatConsumer):
    is_from_admin = True

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not (user.is_staff or user.is_superuser):
            await self.close()
            return

        self.user = user
        self.recipient_user_id = self.scope['url_route']['kwargs'].get('user_id')
        if not self.recipient_user_id:
            await self.close()
            return

        self.room_group_name = f'chat_{self.recipient_user_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        self.admin_group_name = f'chat_{user.id}'
        await self.channel_layer.group_add(self.admin_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.admin_group_name, self.channel_name)

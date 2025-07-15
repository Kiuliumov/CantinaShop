from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_group_name = 'chat_room'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        self.room_group_name = 'chat_room'
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data, **kwargs):
        import json

        data = json.loads(text_data)
        message = data.get('message', '')

        user = self.scope['user']
        if user.is_authenticated:
            account = await self.get_account(user)
            username = user.username
        else:
            account = None
            username = 'Anonymous'

        chat_message = await self.save_message(account, message)
        avatar_url = chat_message.avatar_url if chat_message else ''

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'avatar_url': avatar_url,
                'timestamp': chat_message.timestamp.isoformat() if chat_message else '',
            }
        )

    async def chat_message(self, event):
        import json

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_account(self, user):
        from .models import Account

        try:
            return Account.objects.get(user=user)
        except Account.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, account, message):
        from .models import ChatMessage

        return ChatMessage.objects.create(user=account, message=message)

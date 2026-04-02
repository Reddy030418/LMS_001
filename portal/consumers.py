import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Users have a personal group based on their username
        self.user_group_name = f"user_{self.scope['user'].username}"

        # Join the personal group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Staff can join the 'librarians' group to receive global dashboard notification
        if self.scope["user"].is_staff:
            await self.channel_layer.group_add(
                "librarians",
                self.channel_name
            )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        if hasattr(self, 'scope') and self.scope["user"].is_staff:
            await self.channel_layer.group_discard(
                "librarians",
                self.channel_name
            )

    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        title = event.get('title', 'Notification')
        type = event.get('type_status', 'info') # info, success, warning, error

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'title': title,
            'type': type
        }))

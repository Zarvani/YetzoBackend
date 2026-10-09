import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'tracking_{self.booking_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (from the Professional's app)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        latitude = text_data_json.get('latitude')
        longitude = text_data_json.get('longitude')

        # Send message to room group (to the Customer's app)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude
            }
        )

    # Receive message from room group
    async def location_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'latitude': latitude,
            'longitude': longitude
        }))

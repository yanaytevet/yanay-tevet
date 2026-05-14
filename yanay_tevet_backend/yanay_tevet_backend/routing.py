from django.urls import path

from users.consumers.main_websocket_consumer import MainWebsocketConsumer

websocket_urlpatterns = [
   path(r'ws/socket/', MainWebsocketConsumer.as_asgi()),
]

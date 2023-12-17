from django.urls import re_path
from StocksApp import consumers

websocket_urlpatterns = [
    re_path(r'ws/task-status/', consumers.TaskStatusConsumer.as_asgi()),
]
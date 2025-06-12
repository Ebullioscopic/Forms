from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/forms/<str:share_code>/', consumers.FormCollaborationConsumer.as_asgi()),
]

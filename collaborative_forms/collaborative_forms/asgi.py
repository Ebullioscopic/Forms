"""
ASGI config for collaborative_forms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_forms.settings')

# Initialize Django ASGI application early to ensure the AppRegistry is populated
# before importing consumers that access models
django_asgi_app = get_asgi_application()

# NOW import channels and your routing modules
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import forms.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            forms.routing.websocket_urlpatterns
        )
    ),
})


# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# import massmeters.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import massmeters.routing


# application = ProtocolTypeRouter({
#     # "websocket": URLRouter([
#     #     massmeters.routing.websocket_urlpatterns
#     # ]),
# })

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            massmeters.routing.websocket_urlpatterns
        )
    ),
})
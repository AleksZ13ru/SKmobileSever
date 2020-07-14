# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# import massmeters.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import subscribe.routing


# application = ProtocolTypeRouter({
#     # "websocket": URLRouter([
#     #     massmeters.routing.websocket_urlpatterns
#     # ]),
# })

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            subscribe.routing.websocket_urlpatterns
        )
    ),
})
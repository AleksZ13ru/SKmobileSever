from django.contrib import admin
from .models import MassMeter, Status, Document, Message, Crash

admin.site.register(MassMeter)
admin.site.register(Status)
admin.site.register(Document)
admin.site.register(Message)
admin.site.register(Crash)

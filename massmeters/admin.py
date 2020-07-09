from django.contrib import admin
from .models import MassMeter, Status, Document, Message, Crash, Event

admin.site.register(MassMeter)
admin.site.register(Status)
admin.site.register(Document)
admin.site.register(Message)
admin.site.register(Crash)
admin.site.register(Event)
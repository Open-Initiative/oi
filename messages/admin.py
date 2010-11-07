#coding: utf-8
# Admin manager

from oi.messages.models import Message,Expert,PromotedMessage
from django.contrib import admin

admin.site.register(Message)
admin.site.register(Expert)
admin.site.register(PromotedMessage)

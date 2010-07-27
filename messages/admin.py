#coding: utf-8
# Admin manager

from oi.messages.models import Message,Expert
from django.contrib import admin

admin.site.register(Message)
admin.site.register(Expert)
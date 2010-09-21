#coding: utf-8
# Admin manager

from oi.users.models import UserProfile,PersonalMessage
from django.contrib import admin

admin.site.register(UserProfile)
admin.site.register(PersonalMessage)

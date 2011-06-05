#coding: utf-8
# Admin manager

from oi.users.models import UserProfile,PersonalMessage,Payment
from django.contrib import admin

class PaymentAdmin(admin.ModelAdmin):
    list_display=('id','user','amount','transaction_date', 'project')
    pass

admin.site.register(UserProfile)
admin.site.register(PersonalMessage)
admin.site.register(Payment, PaymentAdmin)

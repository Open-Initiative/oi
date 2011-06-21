#coding: utf-8
# Admin manager

from oi.users.models import UserProfile, PersonalMessage, Payment, Prospect
from django.contrib import admin

class PaymentAdmin(admin.ModelAdmin):
    list_display=('id','user','amount','transaction_date', 'project')
    pass

class ProspectAdmin(admin.ModelAdmin):
    list_display=('id','email','name','kompassId', 'contacted', 'updated')
    search_fields = ['email']
    pass

admin.site.register(UserProfile)
admin.site.register(PersonalMessage)
admin.site.register(Prospect, ProspectAdmin)
admin.site.register(Payment, PaymentAdmin)

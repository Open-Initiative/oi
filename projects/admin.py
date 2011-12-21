#coding: utf-8
# Admin manager

from oi.projects.models import Project,Spec,Bid,PromotedProject
from django.contrib import admin

class ProjectAdmin(admin.ModelAdmin):
    radio_fields = {'state':admin.HORIZONTAL}
    list_display=('title','parent',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Spec)
admin.site.register(Bid)
admin.site.register(PromotedProject)

#coding: utf-8
# Admin manager

from oi.projects.models import Project,Spec,Bid,PromotedProject
from django.contrib import admin

admin.site.register(Project)
admin.site.register(Spec)
admin.site.register(Bid)
admin.site.register(PromotedProject)

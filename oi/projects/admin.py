#coding: utf-8
# Admin manager

from oi.projects.models import Project,Spec,Bid,PromotedProject,ProjectACL,Release
from django.contrib import admin
from django.utils.translation import ugettext as _

class SpecInline(admin.TabularInline):
    model = Spec
    extra = 0

class ACLInline(admin.TabularInline):
    model = ProjectACL
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    list_display=('__unicode__','parent','master','public')
    list_per_page = 200
    list_editable = ('public',)
    date_hierarchy = 'created'
    actions = ['compute_descendants']
    search_fields = ['title']
#    list_filter = ('is_staff', 'company')

    raw_id_fields = ('parent',)
    radio_fields = {'state':admin.HORIZONTAL}
    inlines = [SpecInline,ACLInline]

    def compute_descendants(self, request, prjqueryset):
        for prj in prjqueryset:
            for task in prj.descendants.all():
                task.save()
        self.message_user(request, "OK")
    compute_descendants.short_description = _("Recompute all descendants")

admin.site.register(Project, ProjectAdmin)
admin.site.register(Spec)
admin.site.register(Bid)
admin.site.register(PromotedProject)
admin.site.register(Release)

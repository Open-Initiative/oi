from django.contrib import admin
from oi.prjnotify.models import NoticeType, NoticeSetting, Notice, Observer

class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'display', 'description')

class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'notice_type', 'medium')

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notice_type', 'added', 'unseen', 'archived')

class NoticeInline(admin.TabularInline):
    model = Notice
    extra = 0

class ObserverAdmin(admin.ModelAdmin):
    inlines = [NoticeInline]

admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(Observer, ObserverAdmin)

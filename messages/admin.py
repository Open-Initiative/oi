#coding: utf-8
# Admin manager

from oi.messages.models import Message,Expert,PromotedMessage
from django.contrib import admin


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('ancestors',)
    filter_horizontal = ('related',)
    raw_id_fields = ('author','parent',)
    list_display=('title', 'author', 'children_nb', 'created', 'rfp')
    list_filter = ('rfp',)
    search_fields = ('title', 'author__username')

    def children_nb(self, obj):
        return ("%s"%obj.children.count() )
    children_nb.short_description = 'Nombre de réponses'
    
admin.site.register(Message, MessageAdmin)
admin.site.register(Expert)
admin.site.register(PromotedMessage)

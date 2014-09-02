from django.conf.urls import *

from oi.prjnotify.views import notices, mark_all_seen, feed_for_user, single, notice_settings, save_observer

urlpatterns = patterns('',
    url(r'^$', notices, name="notification_notices"),
    url(r'^settings/$', notice_settings, name="notification_notice_settings"),
    url(r'^settings/(?P<id>\d+)/save$', save_observer, name="notification_save_observer"),
#    url(r'^(\d+)/$', single, name="notification_notice"),
#    url(r'^feed/$', feed_for_user, name="notification_feed_for_user"),
#    url(r'^mark_all_seen/$', mark_all_seen, name="notification_mark_all_seen"),
)

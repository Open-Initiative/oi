#!/usr/bin/python
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = "oi.settings"
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, os.path.dirname(_PROJECT_DIR))

from rfc822 import mktime_tz, parsedate_tz
from datetime import datetime
from urllib2 import urlopen
from xml.dom.minidom import parse
from django.db.models import get_model
from django.utils.translation import get_language, activate, ugettext as _
from oi.settings import NOTIFICATION_LANGUAGE_MODULE, LANGUAGE_CODE
from oi.helpers import OI_SCORE_DEFAULT_RELEVANCE
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape
from oi.users.models import UserProfile

users = UserProfile.objects.exclude(rss_feed="")
for user in users:
    try:
        print user.user.username
        app_label, model_name = NOTIFICATION_LANGUAGE_MODULE.split('.')
        model = get_model(app_label, model_name)
        language_model = model._default_manager.get(user__id__exact=user.id)
        if hasattr(language_model, 'language'):
            language = language_model.language
        else:
            language = LANGUAGE_CODE
        print language_model.language
        activate(language)

        nbitem = 0
        xml = parse(urlopen(user.rss_feed))
        feed_date = datetime.now()
        for channel in xml.getElementsByTagName("channel"):
            channelname = channel.getElementsByTagName("title")[0].firstChild.data
            for item in channel.getElementsByTagName("item"):
                msg={}
                for node in item.childNodes:
                    if node.firstChild:
                        if node.nodeName == "pubDate":
                            pubDate = datetime.fromtimestamp(mktime_tz(parsedate_tz(node.firstChild.data)))
                            if feed_date > pubDate > (user.last_feed or datetime.min):
                                msg['publish'] = True
                        else:
                            msg[node.nodeName] = node.firstChild.data
                if msg.get('publish'):
                    text = oiescape(u'%s : <p>%s</p><a href="%s">%s %s</a>'%(msg['title'], msg['description'], msg['link'], _("Published on"), channelname))
                    Message.objects.create(title=msg['title'], text=text, public=True, author=user.user, relevance=OI_SCORE_DEFAULT_RELEVANCE, parent=user.blog)
                    nbitem += 1
                    
    except Exception as e:
        print "erreur du flux de %s"%user.user.username
        print type(e)
        print e
        print msg['title']
    finally:
        user.last_feed = feed_date
        user.save()
        print "%s items"%nbitem

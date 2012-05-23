from datetime import datetime, timedelta
try:
    import cPickle as pickle
except ImportError:
    import pickle
from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, get_language, activate
from oi.helpers import OI_READ

# if this gets updated, the create() method below needs to be as well...
NOTICE_MEDIA = (("1", _("Email")),)

class NoticeType(models.Model):
    label = models.CharField(_('label'), max_length=40)
    display = models.CharField(_('display'), max_length=50)
    description = models.CharField(_('description'), max_length=100)

    @classmethod
    def register(cls, label, display, description):
        """Creates a new NoticeType"""
        notice_type, created = NoticeType.objects.get_or_create(label=label)
        if created:
            print "Created %s NoticeType" % label
        if display != notice_type.display or description != notice_type.description:
            notice_type.display = display
            notice_type.description = description
            notice_type.save()
            if not created:
                print "Updated %s NoticeType" % label
    
    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")

class Observer(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    added = models.DateTimeField(_('added'), auto_now_add=True)
    use_default = models.BooleanField(default=True)
    last_notice = models.DateTimeField(null=True)
    send_every = models.IntegerField(default=3600)
    project = models.ForeignKey("projects.Project", null=True, blank=True)
    
    def should_send(self):
        """determines if the notice should be sent now or later"""
        if self.use_default:
            observer = self.user.get_profile().get_default_observer()
        else:
            observer = self
        next_notice = (observer.last_notice or datetime.min) + timedelta(seconds=observer.send_every)
        return next_notice < datetime.now() and self.user.email and self.user.is_active
    
    def notify(self, label, project=None, param="", sender=None):
        """Adds notifications for the given list of users"""
        if isinstance(sender, AnonymousUser):
            sender = None
        if project and project.has_perm(self.user, OI_READ):
            notice_type = NoticeType.objects.get(label=label)
            notice = Notice.objects.create(recipient=self.user, project=project, observer=self,
                notice_type=notice_type, sender=sender, param=param)
            if self.get_setting(notice_type).send:
                if self.should_send(): # Email
                    self.send()
            else:
                notice.sent = datetime.now()
                notice.save()
    
    def send(self):
        notices = self.notice_set.filter(sent=None)
        if not notices:
            return
        # the language is to be temporarily switched to the recipient's language
        current_language = get_language()
        activate(self.user.get_profile().language)
        
        # update context with site information
        current_site = "%s://%s"%(getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http"), Site.objects.get_current())
        context = Context({"recipient": self.user, "notification_url": reverse("notification_notices"), 'current_site': current_site, 'observed_project': self.project})
        
        # e-mail data
        subject = _('Notifications on %s')%(self.project.title if self.project else _('your account'))
        body = render_to_string('notification/email_body.txt', {'notices': notices, 'format': 'txt'}, context)
        body_html = render_to_string('notification/email_body.html', {'notices':notices, 'format': 'html'}, context)
        
        msg = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [self.user.email])
        msg.attach_alternative(body_html, "text/html")
        msg.send()
        
        notices.update(sent=datetime.now())
        if self.use_default:
            observer = self.user.get_profile().get_default_observer()
        else:
            observer = self
        observer.last_notice = datetime.now()
        observer.save()
        # reset environment to original language
        activate(current_language)
    
    def get_setting(self, notice_type):
        """gets a setting for a given notice type"""
        if self.use_default:
            observer = self.user.get_profile().get_default_observer()
        else:
            observer = self
        setting, created = observer.noticesetting_set.get_or_create(notice_type=notice_type)
        return setting
    
    def __unicode__(self):
        return u"%s's observer on %s"%(self.user, self.project or "all projects")
        
    class Meta:
        verbose_name = _("observer")
        unique_together = ("user", "project")

class NoticeSetting(models.Model):
    """Indicates, for a given observer, whether to send notifications and how"""
    observer = models.ForeignKey(Observer, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    medium = models.CharField(_('medium'), max_length=1, choices=NOTICE_MEDIA)
    send = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("observer", "notice_type")

class NoticeManager(models.Manager):
    def notices_for(self, user, archived=False, unseen=None, on_site=None, project=None):
        """
        returns Notice objects for the given user.
        parameters : archived (True/False), unseen (True/False/None)
        """
        lookup_kwargs = {"recipient": user}
        qs = self.filter(recipient=user)
        if not archived:
            self.filter(archived=archived)
        if unseen is not None:
            qs = qs.filter(unseen=unseen)
        if on_site is not None:
            qs = qs.filter(on_site=on_site)
        if project is not None:
            qs = qs.filter(project=project)
        return qs

    def unseen_count_for(self, recipient, **kwargs):
        """
        returns the number of unseen notices for the given user but does not
        mark them seen!
        """
        return self.notices_for(recipient, unseen=True, **kwargs).count()
    
    def received(self, recipient, **kwargs):
        """returns notices the given recipient has recieved."""
        kwargs["sent"] = False
        return self.notices_for(recipient, **kwargs)
    
    def sent(self, sender, **kwargs):
        """returns notices the given sender has sent"""
        kwargs["sent"] = True
        return self.notices_for(sender, **kwargs)

class Notice(models.Model):
    recipient = models.ForeignKey(User, related_name='recieved_notices', verbose_name=_('recipient'))
    sender = models.ForeignKey(User, null=True, related_name='sent_notices', verbose_name=_('sender'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    param = models.TextField(blank=True)
    added = models.DateTimeField(_('added'), auto_now_add=True)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    sent = models.DateTimeField(null=True)
    on_site = models.BooleanField(_('on site'), default=True)
    project = models.ForeignKey("projects.Project")
    observer = models.ForeignKey(Observer)
    objects = NoticeManager()

    def __unicode__(self):
        return self.notice_type.label

    def archive(self):
        self.archived = True
        self.save()
    
    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")
    
    def get_absolute_url(self):
        return ("notification_notice", [str(self.pk)])
    get_absolute_url = models.permalink(get_absolute_url)

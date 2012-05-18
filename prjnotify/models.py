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

def notify(users, label, project=None, extra_context={}, on_site=True, sender=None):
    """Adds notifications for the given list of users"""
    if isinstance(sender, AnonymousUser):
        sender = None

    for user in users:
        if project and project.has_perm(user, OI_READ):
            notice = Notice.objects.create(recipient=user, project=project, on_site=on_site,
                notice_type=NoticeType.objects.get(label=label), sender=sender)
            if NoticeSetting.get_notification_setting(user, notice.notice_type, project).should_send() and user.email and user.is_active: # Email
                notice.send()

class NoticeType(models.Model):
    label = models.CharField(_('label'), max_length=40)
    display = models.CharField(_('display'), max_length=50)
    description = models.CharField(_('description'), max_length=100)
    default = models.IntegerField(_('default'))

    @classmethod
    def register(cls, label, display, description, default=2):
        """Creates a new NoticeType"""
        notice_type, created = NoticeType.objects.get_or_create(label=label)
        if created:
            print "Created %s NoticeType" % label
        if display != notice_type.display or description != notice_type.description or default != notice_type.default:
            notice_type.display = display
            notice_type.description = description
            notice_type.default = default
            notice_type.save()
            if not created:
                print "Updated %s NoticeType" % label
    
    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")

class NoticeSetting(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    medium = models.CharField(_('medium'), max_length=1, choices=NOTICE_MEDIA)
    last_notice = models.DateTimeField(null=True)
    send_every = models.IntegerField(default=3600)
    project = models.ForeignKey("projects.Project", null=True)
    
    def should_send(self):
        return (self.last_notice or datetime.min) + timedelta(seconds=self.send_every) < datetime.now()
    
    @classmethod
    def get_setting(cls, user, notice_type, project=None):
        try:
            return NoticeSetting.objects.get(user=user, notice_type=notice_type, project=project)
        except NoticeSetting.DoesNotExist:
            setting, created = NoticeSetting.objects.get_or_create(user=user, notice_type=notice_type, project=None)
            return setting
    
    def __unicode__(self):
        return u"%s's notification settings for %s on %s"%(self.user, self.notice_type, self.project or "all projects")
    
    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("user", "notice_type", "project")

class Notice(models.Model):
    recipient = models.ForeignKey(User, related_name='recieved_notices', verbose_name=_('recipient'))
    sender = models.ForeignKey(User, null=True, related_name='sent_notices', verbose_name=_('sender'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    added = models.DateTimeField(_('added'), default=datetime.now)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    sent = models.DateTimeField(null=True)
    on_site = models.BooleanField(_('on site'))
    project = models.ForeignKey("projects.Project")
    objects = NoticeManager()

    def __unicode__(self):
        return self.render()

    def archive(self):
        self.archived = True
        self.save()
    
    def render(self):
        return render_to_string(('notification/%s/%s' % (self.notice_type.label, 'notice.html'), 'notification/%s' % format),
            context_instance=Context({"recipient": self.recipient, "sender": self.sender, "notice": ugettext(self.notice_type.display),}))

    def send(self):
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        current_language = get_language() #the language is to be temporarily switched to the recipient's language
        activate(self.recipient.get_profile().language)
        
        formats = ('short.txt', 'full.txt', 'notice.html', 'full.html',) # TODO make formats configurable
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = Site.objects.get_current()
        notices_url = u"%s://%s%s" % (protocol, unicode(current_site), reverse("notification_notices"),)

        # update context with user specific translations
        context = Context({"recipient": self.recipient, "sender": self.sender, "notice": ugettext(self.notice_type.display),
            "notices_url": notices_url, "current_site": current_site,})
        
        self.sent = datetime.now()
        self.save()
        
        # get formated messages
        messages = self.get_formatted_messages(formats, context)
        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt', {'message': messages['short.txt'],}, context).splitlines())
        body = render_to_string('notification/email_body.txt', {'message': messages['full.txt'],}, context)
        body_html = render_to_string('notification/email_body.html', {'message': messages['full.html'],}, context)
        
        msg = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [self.recipient.email])
        msg.attach_alternative(body_html, "text/html")
    
        # reset environment to original language
        activate(current_language)
        return msg.send()

    def get_formatted_messages(self, formats, context):
        """
        Returns a dictionary with the format identifier as the key. The values are
        are fully rendered templates with the given context.
        """
        format_templates = {}
        for format in formats:
            # conditionally turn off autoescaping for .txt extensions in format
            if format.endswith(".txt"):
                context.autoescape = False
            else:
                context.autoescape = True
            format_templates[format] = render_to_string((
                'notification/%s/%s' % (self.label, format),
                'notification/%s' % format), context_instance=context)
        return format_templates
    
    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

    def get_absolute_url(self):
        return ("notification_notice", [str(self.pk)])
    get_absolute_url = models.permalink(get_absolute_url)

class NoticeManager(models.Manager):
    def notices_for(self, user, archived=False, unseen=None, on_site=None, sent=False):
        """
        returns Notice objects for the given user.

        If archived=False, it only include notices not archived.
        If archived=True, it returns all notices for that user.

        If unseen=None, it includes all notices.
        If unseen=True, return only unseen notices.
        If unseen=False, return only seen notices.
        """
        if sent:
            lookup_kwargs = {"sender": user}
        else:
            lookup_kwargs = {"recipient": user}
        qs = self.filter(**lookup_kwargs)
        if not archived:
            self.filter(archived=archived)
        if unseen is not None:
            qs = qs.filter(unseen=unseen)
        if on_site is not None:
            qs = qs.filter(on_site=on_site)
        return qs

    def unseen_count_for(self, recipient, **kwargs):
        """
        returns the number of unseen notices for the given user but does not
        mark them seen
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

class ObservedItemManager(models.Manager):
    def all_for(self, observed, signal):
        """
        Returns all ObservedItems for an observed object,
        to be sent when a signal is emited.
        """
        content_type = ContentType.objects.get_for_model(observed)
        observed_items = self.filter(content_type=content_type, object_id=observed.id, signal=signal)
        return observed_items

    def get_for(self, observed, observer, signal):
        content_type = ContentType.objects.get_for_model(observed)
        observed_item = self.get(content_type=content_type, object_id=observed.id, user=observer, signal=signal)
        return observed_item

class ObservedItem(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    observed_object = generic.GenericForeignKey('content_type', 'object_id')
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    added = models.DateTimeField(_('added'), default=datetime.now)

    # the signal that will be listened to send the notice
    signal = models.TextField(verbose_name=_('signal'))
    objects = ObservedItemManager()

    class Meta:
        ordering = ['-added']
        verbose_name = _('observed item')
        verbose_name_plural = _('observed items')

    def send_notice(self, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context.update({'observed': self.observed_object})
        send([self.user], self.notice_type.label, extra_context)

def observe(observed, observer, notice_type_label, signal='post_save'):
    """ Create a new ObservedItem.
    To be used by applications to register a user as an observer for some object. """
    notice_type = NoticeType.objects.get(label=notice_type_label)
    observed_item = ObservedItem(user=observer, observed_object=observed, notice_type=notice_type, signal=signal)
    observed_item.save()
    return observed_item

def stop_observing(observed, observer, signal='post_save'):
    """Remove an observed item."""
    observed_item = ObservedItem.objects.get_for(observed, observer, signal)
    observed_item.delete()

def send_observation_notices_for(observed, signal='post_save', extra_context=None):
    """Send a notice for each registered user about an observed object."""
    if extra_context is None:
        extra_context = {}
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        observed_item.send_notice(extra_context)
    return observed_items

def is_observing(observed, observer, signal='post_save'):
    if isinstance(observer, AnonymousUser):
        return False
    try:
        observed_items = ObservedItem.objects.get_for(observed, observer, signal)
        return True
    except ObservedItem.DoesNotExist:
        return False
    except ObservedItem.MultipleObjectsReturned:
        return True

def handle_observations(sender, instance, *args, **kw):
    send_observation_notices_for(instance)

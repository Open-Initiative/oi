from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import feed
from django.views.generic.simple import direct_to_template

from oi.prjnotify.models import Notice, NoticeType, NoticeSetting, Observer
from oi.prjnotify.decorators import basic_auth_required, simple_basic_auth_callback
from oi.prjnotify.feeds import NoticeUserFeed
from oi.projects.models import Project

from django.utils.translation import ugettext as _


@basic_auth_required(realm='Notices Feed', callback_func=simple_basic_auth_callback)
def feed_for_user(request):
    """
    An atom feed for all unarchived :model:`notification.Notice`s for a user.
    """
    url = "feed/%s" % request.user.username
    return feed(request, url, {
        "feed": NoticeUserFeed,
    })

@login_required
def notices(request):
    project = Project.objects.get(id=request.GET["project"]) if request.GET.get("project") else None
    notices = Notice.objects.notices_for(request.user, on_site=True, project=project)
    return render_to_response("notification/notices.html", {"notices": notices, "see_archived": request.GET.get("see")=="all", 'project': project}, context_instance=RequestContext(request))

@login_required
def notice_settings(request):
    default = request.user.get_profile().get_default_observer()
    observers = Observer.objects.filter(user=request.user)
    #ensures settings objects exists when the observer doesn't use the default configuration
    for observer in observers.filter(use_default=False):
        for notice_type in NoticeType.objects.all():
            observer.get_setting(notice_type)
    return direct_to_template(request, template="notification/settings.html", extra_context={'default_observer': default, 'observers': observers})


@login_required
def single(request, id, mark_seen=True):
    """
    Detail view for a single :model:`notification.Notice`.
    Template: :template:`notification/single.html`
    Context: notice
            The :model:`notification.Notice` being viewed
    Optional arguments:  mark_seen
            If ``True``, mark the notice as seen if it isn't
            already.  Do nothing if ``False``.  Default: ``True``.
    """
    notice = get_object_or_404(Notice, id=id)
    if request.user == notice.recipient:
        if mark_seen and notice.unseen:
            notice.unseen = False
            notice.save()
        return render_to_response("notification/single.html", {"notice": notice,}, context_instance=RequestContext(request))
    raise Http404


@login_required
def archive(request, noticeid=None, next_page=None):
    """
    Archive a :model:`notices.Notice` if the requesting user is the
    recipient or if the user is a superuser.  Returns a
    ``HttpResponseRedirect`` when complete.
    Optional arguments:
        noticeid
            The ID of the :model:`notices.Notice` to be archived.
        next_page
            The page to redirect to when done.
    """
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.recipient or request.user.is_superuser:
                notice.archive()
            else:   # you can archive other users' notices
                    # only if you are superuser.
                return HttpResponseRedirect(next_page)
        except Notice.DoesNotExist:
            return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(next_page)

@login_required
def delete(request, noticeid=None, next_page=None):
    """
    Delete a :model:`notices.Notice` if the requesting user is the recipient
    or if the user is a superuser.  Returns a ``HttpResponseRedirect`` when
    complete.
    Optional arguments:
        noticeid
            The ID of the :model:`notices.Notice` to be archived.
        next_page
            The page to redirect to when done.
    """
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.recipient or request.user.is_superuser:
                notice.delete()
            else:   # you can delete other users' notices
                    # only if you are superuser.
                return HttpResponseRedirect(next_page)
        except Notice.DoesNotExist:
            return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(next_page)

@login_required
def mark_all_seen(request):
    """
    Mark all unseen notices for the requesting user as seen.  Returns a
    ``HttpResponseRedirect`` when complete. 
    """
    for notice in Notice.objects.notices_for(request.user, unseen=True):
        notice.unseen = False
        notice.save()
    return HttpResponseRedirect(reverse("notification_notices"))
 
@login_required   
def save_observer(request, id):
    """save observer modification"""
    observer = Observer.objects.get(id=id)
    
    if request.POST.get("frequency"):
        observer.send_every = request.POST["frequency"]
    if request.POST.get("use_default"):
        observer.use_default = request.POST["use_default"]
    if request.POST.get("noticeField"):
        observer.noticesetting_set.filter(notice_type__label=POST["noticeField"]).update(send=request.POST["send"])
    if observer:
        observer.save()
        return HttpResponse(_("Modification saved"))
    

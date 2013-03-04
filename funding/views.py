from django.http import Http404
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project, OINeedsPrjPerms
from oi.helpers import OI_READ


def get_feature(request, id):
    task = Project.objects.get(id=id)
    if not task.has_perm(request.user, OI_READ):
        raise Http404
    return direct_to_template(request, template="funding/feature.html", extra_context={'object': task.master, 'task': task})

from django.http import Http404
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project, OINeedsPrjPerms
from oi.helpers import OI_READ

@OINeedsPrjPerms(OI_READ)
def get_feature(request, id, taskid):
    project = Project.objects.get(id=id)
    task = Project.objects.get(id=taskid)
    if not task.has_perm(request.user, OI_READ) or not task.master==project:
        raise Http404
    return direct_to_template(request, template="funding/feature.html", extra_context={'object': project, 'task': task})

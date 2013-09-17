from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from oi.projects.models import Project, OINeedsPrjPerms, Spec
from oi.helpers import OI_READ, OI_WRITE, SPEC_TYPES

def get_project(request, id):
    """get the main project page"""
    project = get_object_or_404(Project, pk=id)
    if project.parent:
        return HttpResponseRedirect('/funding/%s'%project.master.id)
    return direct_to_template(request, template="funding/project_detail.html", extra_context={'object': project, 'types': SPEC_TYPES})
    
def get_feature(request, id):
    """gets the feature block"""
    task = Project.objects.get(id=id)
    if not task.has_perm(request.user, OI_READ):
        raise Http404
    return direct_to_template(request, template="funding/feature.html", extra_context={'object': task.master, 'task': task})
    
@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec in a feature popup"""
    spec=None
    order = request.GET.get("specorder")
    if specid!='0':
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        order = spec.order
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'types':SPEC_TYPES, 'specorder':order}
    return object_detail(request, queryset=Project.objects, object_id=id, template_object_name='project', template_name='funding/spec/editspec.html', extra_context=extra_context)

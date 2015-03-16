from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, DetailView
from oi.projects.models import Project, OINeedsPrjPerms, Spec, Reward, RewardForm
from oi.helpers import OI_READ, OI_WRITE, SPEC_TYPES, OI_ACCEPTED

def get_project(request, id):
    """get the main project page"""
    extra_context = {}
    forms = {}
    project = get_object_or_404(Project, pk=id)
    if project.parent:
        return HttpResponseRedirect('/funding/%s'%project.master.id)
    
    for reward in project.reward_set.all():
        forms['reward_form_%s'%reward.id] = RewardForm(instance=project.reward_set.all().get(id=reward.id))
    
    extra_context['forms'] = forms
    extra_context['reward_form'] = RewardForm() 
    extra_context['object'] = project
    extra_context['types'] = SPEC_TYPES
    return TemplateResponse(request, "funding/project_detail.html", extra_context)
    
def get_feature(request, id):
    """gets the feature block"""
    task = Project.objects.get(id=id)
    if not task.has_perm(request.user, OI_READ):
        raise Http404
    extra_context={'object': task.master, 'task': task}
    return TemplateResponse(request, "funding/feature.html", extra_context)
    
@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec in a feature popup"""
    spec=None
    order = request.GET.get("specorder")
    if specid!='0':
        spec = get_object_or_404(Spec, id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        order = spec.order
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'specorder':order, 'project':Project.objects.get(id=id)}
    return TemplateResponse(request, 'funding/spec/editspec.html', extra_context)
    
@OINeedsPrjPerms(OI_WRITE)
def editspecdetails(request, id, specid):
    """Edit template of a spec detail, ie: text, image, file..."""
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    spec=None
    if specid!='0':
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a task already started"), status=431)
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
    extra_context = {'user': request.user, 'divid': request.GET["divid"], 'project':project, 'spec':spec}
    return TemplateResponse(request, 'funding/spec/edit_type%s.html'%(type), extra_context)
    

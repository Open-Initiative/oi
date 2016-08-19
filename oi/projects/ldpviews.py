from django.contrib.sites.models import get_current_site
from django.core import serializers
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from oi.helpers import OI_READ, OI_ANSWER, OI_BID, OI_MANAGE, OI_WRITE, OI_ALL_PERMS, jsonld_array
from oi.projects.models import Project, Spec, OINeedsPrjPerms, Release

from rest_framework import viewsets
from oi.projects.serializers import ProjectSerializer


#def exception_handler(exc):
#    print 2
#    print exc
#    return HttpResponse({'detail' : exc, 'args' : ['arg1', 'arg2']}, status = 417)

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def dispatch(self, request, *args, **kwargs):
        response = super(ProjectViewSet, self).dispatch(request, *args, **kwargs)
        response["Content-Type"] = "application/ld+json"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST,PUT"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        response["Accept-Post"] = "application/ld+json"
        return response

@OINeedsPrjPerms(OI_READ)
def ldpspec(request, id, specid):
    """Return jsonLd object"""
    project = get_object_or_404(Project, id=id)
    response = render_to_response("ldp/spec.json", {
        "spec": get_object_or_404(Spec, id=specid),
        "current_site" : get_current_site(request)
    })
    response["Content-Type"] = "application/ld+json"
    response["Access-Control-Allow-Origin"] = "*"
    return response

@OINeedsPrjPerms(OI_READ)
def ldprelease(request, id, releaseid):
    """Return jsonLd object"""
    project = get_object_or_404(Project, id=id)
    response = render_to_response("ldp/release.json", {
        "release":  get_object_or_404(Release, id=releaseid),
        "current_site" : get_current_site(request),
    })
    response["Content-Type"] = "application/ld+json"
    response["Access-Control-Allow-Origin"] = "*"
    return response

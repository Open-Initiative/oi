from django.http import HttpResponse
from ldprest.views import LDPView
from oi.projects.models import Project, Spec, OINeedsPrjPerms, Release


def exception_handler(exc):
    print "Exception"
    print exc
    return HttpResponse({'detail' : exc, 'args' : ['arg1', 'arg2']}, status = 417)

class ProjectView(LDPView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    fields = ('@id', 'title', 'author', 'state', 'target', 'ldp:contains', 'descendants', 'spec_set', 'message_set', 'release_set')

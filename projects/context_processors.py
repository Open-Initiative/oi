from django.contrib.sites.models import Site
from oi.helpers import OI_PRJ_STATES, OI_PRJ_PHASES, OI_COMMISSION
from oi.settings import github_id

def constants(request):
    """return specific constants for templates as a dictionnary."""
    return {'Sites': dict(map(lambda l:map(str, l), Site.objects.values_list("name", "domain"))), 'current_site': Site.objects.get_current(), 'github_id': github_id, 'OI_COMMISSION': OI_COMMISSION, 'OI_PRJ_STATES': OI_PRJ_STATES, 'OI_PRJ_PHASES': OI_PRJ_PHASES}


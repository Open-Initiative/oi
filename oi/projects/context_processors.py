from django.conf import settings
from django.contrib.sites.models import Site
from oi.settings_common import OI_GITHUB_ID
from oi.helpers import OI_PRJ_STATES, OI_PRJ_PHASES, OI_COMMISSION, SPEC_TYPES

def constants(request):
    """return specific constants for templates as a dictionnary."""
    return {'Sites': dict(map(lambda l:map(str, l), Site.objects.values_list("name", "domain"))), 'current_site': Site.objects.get_current(), 'github_id': OI_GITHUB_ID, 'OI_COMMISSION': OI_COMMISSION, 'OI_PRJ_STATES': OI_PRJ_STATES, 'OI_PRJ_PHASES': OI_PRJ_PHASES, 'REDIRECT_URL':settings.REDIRECT_URL, 'types': SPEC_TYPES, 'site_name':settings.SITE_NAME}


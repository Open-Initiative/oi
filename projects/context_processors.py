from oi.helpers import OI_PRJ_STATES, OI_PRJ_PHASES, OI_COMMISSION

def constants(request):
    """return specific constants for templates as a dictionnary."""
    return {'OI_COMMISSION': OI_COMMISSION, 'OI_PRJ_STATES': OI_PRJ_STATES, 'OI_PRJ_PHASES': OI_PRJ_PHASES}


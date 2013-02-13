from django.contrib.sites.models import SiteManager, SITE_CACHE

def oi_get_current(self):
    """
    Returns the current ``Site`` based on the SITE_ID in the
    project's settings. The ``Site`` object is cached the first
    time it's retrieved from the database.
    """
    from django.conf import settings
    try:
        sid = settings.SITE_ID
    except AttributeError:
        sid = None
        try:
            sname = settings.SITE_NAME
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set either the SITE_ID or the SITE_NAME setting to fix this error.")
    if sid:
        try:
            current_site = SITE_CACHE[sid]
        except KeyError:
            current_site = self.get(pk=sid)
            SITE_CACHE[current_site.name] = current_site
            SITE_CACHE[current_site.id] = current_site
    else:
        try:
            current_site = SITE_CACHE[sname]
        except KeyError:
            current_site = self.get(name=sname)
            SITE_CACHE[current_site.name] = current_site
            SITE_CACHE[current_site.id] = current_site

    return current_site

SiteManager.get_current = oi_get_current


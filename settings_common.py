#coding: utf-8
# Common configuration to all platforms
# Django settings for oi project.

from settings_specific import *

MANAGERS = ADMINS

OI_LOG_FILE = HOME_DIR + 'log/oi.log'
PAYMENT_LOG_FILE = HOME_DIR + 'log/payments.log'

from logging.handlers import TimedRotatingFileHandler
class OIPaymentFileHandler(TimedRotatingFileHandler):
    def __init__(self):
        TimedRotatingFileHandler.__init__(self, PAYMENT_LOG_FILE)

class OIFileHandler(TimedRotatingFileHandler):
    def __init__(self):
        TimedRotatingFileHandler.__init__(self, OI_LOG_FILE)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {'format': '%(levelname)s %(asctime)s %(module)s (%(processName)s %(threadName)s) %(funcName)s, line %(lineno)d : %(message)s'},
        'simple': {'format': '%(levelname)s %(message)s'},
    },
    'filters': {},
    'handlers': {
        'null': {'level':'DEBUG', 'class':'django.utils.log.NullHandler',},
        'console':{'level':'DEBUG', 'class':'logging.StreamHandler', 'formatter': 'simple'},
        'mail_admins': {'level': 'ERROR','class': 'django.utils.log.AdminEmailHandler', 'formatter': 'simple'},
        'oi_file': {'level': 'DEBUG','class': 'oi.settings.OIFileHandler', 'formatter': 'verbose'},
        'payment_file': {'level': 'INFO','class': 'oi.settings.OIPaymentFileHandler', 'formatter': 'verbose'},
    },
    'loggers': {
        'django': {'handlers':['null'], 'propagate': True, 'level':'INFO',},
        'django.request': {'handlers': ['mail_admins'], 'level': 'ERROR', 'propagate': False,},
        'oi': {'handlers': ['console','oi_file'], 'level': 'DEBUG',},
        'oi.payments': {'handlers': ['payment_file'], 'level': 'INFO', 'propagate': False,},
        'oi.alerts': {'handlers': ['mail_admins'], 'level': 'ERROR', 'propagate': False,},
    }
}

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = tuple(dict(OI_DOMAINS).values())
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'X-CSRFToken',
)

# Github configuration
github_id = "723cf00e03393afa2f32"
github_secret = "ebf46f0e906b808303f2b6240f5dd6eaf8897c62"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (HOME_DIR + 'oi/locale',)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = HOME_DIR + 'OIFS/'
TEMP_DIR = HOME_DIR + 'tmp/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-bue#^ex11(nq3d%&9+w0cvdvuq*&=3=s7m-%$b57qh5@&xpy)'

# Auth urls
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/logout"

# Haystack configuration
HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_SITECONF = 'oi.search_sites'
HAYSTACK_XAPIAN_PATH = HOME_DIR + 'indexes'

# User profile model
AUTH_PROFILE_MODULE = 'users.UserProfile'
NOTIFICATION_LANGUAGE_MODULE = 'users.UserProfile'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "oi.projects.context_processors.constants",
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
HOME_DIR = '/home/oi/'

ADMINS = (('Sylvain Le Bon', 'lebon.sylvain@gmail.com'),)

#Database configuration
DATABASES ={'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': 'OI', 'USER': 'root', 'PASSWORD': '4mcoufq9', 'HOST':'', 'PORT': ''}}

# SMTP configuration    
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/oimessages' # change this to a proper location
DEFAULT_FROM_EMAIL = 'admin@openinitiative.com'

# For DebugToolbarMiddleware
INTERNAL_IPS = ('192.168.56.1',)

# For Payment
PAYMENT_ACTION = 'https://secure.ogone.com/ncol/test/orderstandard_utf8.asp'
SHA_KEY = 'Kp3Cjf6rKp3Cjf6r'
SHASIGN_NAME = 'SHASIGN'

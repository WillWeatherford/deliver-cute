"""Overwrite and add settings specifically for production deployed instance."""
from delivercute.settings import *

DEBUG = False
ALLOWED_HOSTS.extend(
    ['.us-west-2.compute.amazonaws.com',
     '.will-weatherford.com',
     ]
)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = ()

SITE_URL = 'http://delivercute.will-weatherford.com'

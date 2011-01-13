from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    TCM_ADMIN_USER = settings.TCM_ADMIN_USER
except AttributeError:
    raise ImproperlyConfigured("TCM_ADMIN_USER setting is required.")

try:
    TCM_ADMIN_PASS = settings.TCM_ADMIN_PASS
except AttributeError:
    raise ImproperlyConfigured("TCM_ADMIN_PASS setting is required.")

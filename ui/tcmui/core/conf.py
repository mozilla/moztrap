from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

for name in [
    "TCM_API_BASE",
    "TCM_ADMIN_USER",
    "TCM_ADMIN_PASS",
    "TCM_COMPANY_ID",
    "TCM_NEW_USER_ROLE_ID",
    ]:
    try:
        locals()[name] = getattr(settings, name)
    except AttributeError:
        raise ImproperlyConfigured("%s setting is required." % name)

HTTPS_STS_SECONDS = getattr(settings, "HTTPS_STS_SETTINGS", 0)

"""
Auth-related context processors.

"""
from django.conf import settings


def browserid(request):
    return {"USE_BROWSERID": settings.USE_BROWSERID}

"""
Authentication view decorators.

"""
from django.conf import settings

from django.contrib.auth.decorators import login_required



def login_maybe_required(viewfunc):
    """no-op if settings.ALLOW_ANONYMOUS_ACCESS, else login_required"""
    if settings.ALLOW_ANONYMOUS_ACCESS:
        return viewfunc
    return login_required(viewfunc)

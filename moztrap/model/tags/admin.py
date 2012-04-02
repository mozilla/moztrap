"""
Admin config for tags.

"""
from django.contrib import admin

from ..mtadmin import MTModelAdmin
from . import models



admin.site.register(models.Tag, MTModelAdmin)

"""
Admin config for tags.

"""
from django.contrib import admin

from ..ccadmin import CCModelAdmin
from . import models



admin.site.register(models.Tag, CCModelAdmin)

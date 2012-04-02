"""
Admin config for environment models.

"""
from django.contrib import admin

from ..mtadmin import MTModelAdmin, MTTabularInline
from . import models



class ElementInline(MTTabularInline):
    model = models.Element
    extra = 0



# not MTTabularInline because auto-generated through model is not MTModel
class EnvironmentElementInline(admin.TabularInline):
    model = models.Environment.elements.through
    extra = 0



admin.site.register(models.Profile, MTModelAdmin)
admin.site.register(models.Category, MTModelAdmin, inlines=[ElementInline])
admin.site.register(models.Element, MTModelAdmin)
admin.site.register(
    models.Environment, MTModelAdmin,
    inlines=[EnvironmentElementInline], exclude=["elements"])

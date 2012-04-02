"""
Admin config for environment models.

"""
from django.contrib import admin

from ..ccadmin import CCModelAdmin, CCTabularInline
from . import models



class ElementInline(CCTabularInline):
    model = models.Element
    extra = 0



# not CCTabularInline because auto-generated through model is not CCModel
class EnvironmentElementInline(admin.TabularInline):
    model = models.Environment.elements.through
    extra = 0



admin.site.register(models.Profile, CCModelAdmin)
admin.site.register(models.Category, CCModelAdmin, inlines=[ElementInline])
admin.site.register(models.Element, CCModelAdmin)
admin.site.register(
    models.Environment, CCModelAdmin,
    inlines=[EnvironmentElementInline], exclude=["elements"])

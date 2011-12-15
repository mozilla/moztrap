from django.contrib import admin

from . import models



class CaseVersionInline(admin.StackedInline):
    model = models.CaseVersion
    extra = 0


class CaseStepInline(admin.TabularInline):
    model = models.CaseStep
    extra = 0


admin.site.register(models.Suite)
admin.site.register(models.Case, inlines=[CaseVersionInline])
admin.site.register(models.CaseVersion, inlines=[CaseStepInline])

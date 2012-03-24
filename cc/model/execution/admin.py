"""
Admin config for execution models.

"""
from django.contrib import admin

from ..ccadmin import (
    CCModelAdmin, TeamModelAdmin, CCTabularInline, CCStackedInline)
from . import models



class RunCaseVersionInline(CCTabularInline):
    model = models.RunCaseVersion
    extra = 0



class RunSuiteInline(CCTabularInline):
    model = models.RunSuite
    extra = 0



class ResultInline(CCStackedInline):
    model = models.Result
    extra = 0
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status", "started", "completed"),
                    "comment",
                    ("review", "reviewed_on", "reviewed_by"),
                    "exists",
                    ]})]



class StepResultInline(CCTabularInline):
    model = models.StepResult
    extra = 0



class RunAdmin(TeamModelAdmin):
    filter_horizontal = ["environments"]
    fieldsets = [(None, {"fields": [
                    "name",
                    ("productversion", "status"),
                    "description",
                    ("start", "end"),
                    "environments",
                    ]})]
    inlines = [RunSuiteInline, RunCaseVersionInline]



class ResultAdmin(CCModelAdmin):
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status", "started", "completed"),
                    "comment",
                    ("review", "reviewed_on", "reviewed_by"),
                    ]})]
    inlines = [StepResultInline]




admin.site.register(models.Run, RunAdmin)
admin.site.register(
    models.RunCaseVersion, CCModelAdmin, inlines=[ResultInline])
admin.site.register(models.Result, ResultAdmin)

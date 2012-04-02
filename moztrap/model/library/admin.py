"""
Admin config for library models.

"""
from django.contrib import admin

from ..ccadmin import CCModelAdmin, CCTabularInline, CCStackedInline
from . import models



class CaseVersionInline(CCStackedInline):
    model = models.CaseVersion
    extra = 0
    fieldsets = [
        (
            None, {
                "fields": [
                    "productversion",
                    ("name", "status"),
                    "exists",
                    "description",
                    ]
                }
            )
        ]



class CaseAttachmentInline(CCTabularInline):
    model = models.CaseAttachment
    extra = 0



class CaseStepInline(CCTabularInline):
    model = models.CaseStep
    extra = 0



class CaseTagInline(admin.TabularInline):
    model = models.CaseVersion.tags.through
    extra = 0


class SuiteCaseInline(CCTabularInline):
    model = models.SuiteCase
    extra = 0



class CaseVersionAdmin(CCModelAdmin):
    list_display = ["__unicode__", "productversion", "deleted_on"]
    list_filter = ["productversion"]
    inlines = [CaseStepInline, CaseAttachmentInline, CaseTagInline]
    filter_horizontal = ["environments"]
    fieldsets = [
        (
            None, {
                "fields": [
                    "productversion",
                    ("case", "name", "status"),
                    "description",
                    "environments",
                    ]
                }
            )
        ]



admin.site.register(models.Suite, CCModelAdmin)
admin.site.register(
    models.Case, CCModelAdmin, inlines=[CaseVersionInline, SuiteCaseInline])
admin.site.register(models.CaseVersion, CaseVersionAdmin)

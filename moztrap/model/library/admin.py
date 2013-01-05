"""
Admin config for library models.

"""
from django.contrib import admin

from ..mtadmin import MTModelAdmin, MTTabularInline, MTStackedInline
from . import models



class CaseVersionInline(MTStackedInline):
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



class CaseAttachmentInline(MTTabularInline):
    model = models.CaseAttachment
    extra = 0



class CaseStepInline(MTTabularInline):
    model = models.CaseStep
    extra = 0



class CaseTagInline(admin.TabularInline):
    model = models.CaseVersion.tags.through
    extra = 0


class SuiteCaseInline(MTTabularInline):
    model = models.SuiteCase
    extra = 0



class CaseVersionAdmin(MTModelAdmin):
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



class CaseAdmin(MTModelAdmin):
    list_display = ["__unicode__", "product", "deleted_on"]
    list_filter = ["product", "deleted_on"]



admin.site.register(models.Suite, MTModelAdmin)
admin.site.register(
    models.Case, CaseAdmin, inlines=[CaseVersionInline, SuiteCaseInline])
admin.site.register(models.CaseVersion, CaseVersionAdmin)

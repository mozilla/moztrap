from django.contrib import admin

from preferences.admin import PreferencesAdmin

from ..mtadmin import MTTabularInline, MTModelAdmin, TeamModelAdmin
from .models import Product, ProductVersion, CorePreferences, ApiKey



class ProductVersionInline(MTTabularInline):
    model = ProductVersion
    extra = 0


class ProductVersionAdmin(TeamModelAdmin):
    list_filter = ["product"]

    def fix_environments(self, request, queryset):
        for row in queryset:
            row.fix_environments()
    fix_environments.short_description = "Fix envs on un-narrowed"



class ApiKeyAdmin(MTModelAdmin):
    list_display = ["owner", "active", "key"]
    list_filter = ["active"]



admin.site.register(Product, TeamModelAdmin, inlines=[ProductVersionInline])
admin.site.register(ProductVersion, ProductVersionAdmin)
admin.site.register(CorePreferences, PreferencesAdmin)
admin.site.register(ApiKey, ApiKeyAdmin)

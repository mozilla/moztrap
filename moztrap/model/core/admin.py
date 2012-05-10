from django.contrib import admin

from preferences.admin import PreferencesAdmin

from ..mtadmin import MTTabularInline, MTModelAdmin, TeamModelAdmin
from .models import Product, ProductVersion, CorePreferences, ApiKey



class ProductVersionInline(MTTabularInline):
    model = ProductVersion
    extra = 0


class ApiKeyAdmin(MTModelAdmin):
    list_display = ["owner", "active", "key"]
    list_filter = ["active"]



admin.site.register(Product, TeamModelAdmin, inlines=[ProductVersionInline])
admin.site.register(ProductVersion, TeamModelAdmin, list_filter=["product"])
admin.site.register(CorePreferences, PreferencesAdmin)
admin.site.register(ApiKey, ApiKeyAdmin)

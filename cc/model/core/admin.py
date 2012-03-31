from django.contrib import admin

from preferences.admin import PreferencesAdmin

from ..ccadmin import CCTabularInline, TeamModelAdmin
from .models import Product, ProductVersion, CorePreferences



class ProductVersionInline(CCTabularInline):
    model = ProductVersion
    extra = 0



admin.site.register(Product, TeamModelAdmin, inlines=[ProductVersionInline])
admin.site.register(ProductVersion, TeamModelAdmin, list_filter=["product"])
admin.site.register(CorePreferences, PreferencesAdmin)

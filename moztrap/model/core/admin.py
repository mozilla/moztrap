from django.contrib import admin

from preferences.admin import PreferencesAdmin

from ..mtadmin import MTTabularInline, TeamModelAdmin
from .models import Product, ProductVersion, CorePreferences



class ProductVersionInline(MTTabularInline):
    model = ProductVersion
    extra = 0



admin.site.register(Product, TeamModelAdmin, inlines=[ProductVersionInline])
admin.site.register(ProductVersion, TeamModelAdmin, list_filter=["product"])
admin.site.register(CorePreferences, PreferencesAdmin)

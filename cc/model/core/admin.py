from django.contrib import admin

from ..ccadmin import CCTabularInline, TeamModelAdmin
from .models import Product, ProductVersion



class ProductVersionInline(CCTabularInline):
    model = ProductVersion
    extra = 0



admin.site.register(Product, TeamModelAdmin, inlines=[ProductVersionInline])
admin.site.register(ProductVersion, TeamModelAdmin, list_filter=["product"])

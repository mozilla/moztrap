from ..core.filters import LocatorFieldFilter

from .models import ProductList



class ProductFieldFilter(LocatorFieldFilter):
    target = ProductList

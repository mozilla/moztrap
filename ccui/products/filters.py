from ..core.filters import RelatedFieldFilter

from .models import ProductList



class ProductFieldFilter(RelatedFieldFilter):
    target = ProductList

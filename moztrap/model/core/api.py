from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Product, ProductVersion


class ProductResource(ModelResource):

    class Meta:
        queryset = Product.objects.all()
        fields = ["id", "name", "description", "resource_uri"]
        filtering = {"name": (ALL)}


class ProductVersionResource(ModelResource):
    """
    Fetch the versions for the specified test product

    """

    product = fields.ForeignKey(ProductResource, "product")

    class Meta:
        queryset = ProductVersion.objects.all()
        fields = ["id", "version", "codename", "resource_uri"]
        filtering = {
            "version": (ALL),
            "product": (ALL_WITH_RELATIONS),
            }


    def dehydrate(self, bundle):
        product_name = bundle.obj.product.name
        bundle.data['product__name'] = product_name
        return bundle


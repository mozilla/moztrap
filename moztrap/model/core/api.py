from tastypie.resources import ModelResource
from tastypie import fields

from .models import Product, ProductVersion



class ProductVersionResource(ModelResource):
    """
    Fetch the versions for the specified test product

    """

    class Meta:
        queryset = ProductVersion.objects.all()
        fields = ["id", "version", "codename", "resource_uri", "product_name"]


    def dehydrate(self, bundle):
        product_name = bundle.obj.product.name
        bundle.data['product_name'] = product_name
        return bundle


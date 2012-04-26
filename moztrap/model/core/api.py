from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Product, ProductVersion
from .auth import User


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



class ReportResultsAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if request.user.has_perm("Can run tests and report results."):
            return True
        else:
            return False


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        excludes = ['email', 'password', 'is_superuser']
        # Add it here.
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
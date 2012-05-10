from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Product, ProductVersion, ApiKey

from .auth import User



class MTApiKeyAuthentication(ApiKeyAuthentication):


    def get_key(self, user, api_key):
        try:
            ApiKey.objects.get(owner=user, key=api_key, active=True)

        except:
            return self._unauthorized()

        return True



class ReportResultsAuthorization(Authorization):


    def is_authorized(self, request, object=None):
        if request.user.has_perm("execution.EXECUTE"):
            return True
        else:
            return False



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



class UserResource(ModelResource):


    class Meta:
        queryset = User.objects.all()
        fields = ["username", "resource_uri"]

        authentication = MTApiKeyAuthentication()
        # TODO @@@ not clear what kind of auth to use here.
#        authorization = ReportResultsAuthorization()




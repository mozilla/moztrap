from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Product, ProductVersion, ApiKey
from ..environments.api import EnvironmentResource

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
        if request.user.has_perm("execution.execute"):
            return True
        else:
            return False



class ProductVersionResource(ModelResource):
    """
    Fetch the versions for the specified test product

    """

    class Meta:
        queryset = ProductVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "version", "codename", "resource_uri"]
        filtering = {
            "version": ALL,
            }


class ProductResource(ModelResource):

    productversions = fields.ToManyField(
        ProductVersionResource,
        "versions",
        full=True,
        )

    class Meta:
        queryset = Product.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name", "description", "resource_uri"]
        filtering = {"name": ALL}



class ProductVersionEnvironmentsResource(ModelResource):
    """Environments for a specific productversion."""
    environments = fields.ToManyField(
        EnvironmentResource,
        "environments",
        full=True,
        )

    class Meta:
#        resource_name="productversion/environments"
        queryset = ProductVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "version", "codename", "resource_uri"]



class UserResource(ModelResource):
    """
    Return the username of a user only.

    This is used to fill the username field for returned objects.
    """

    class Meta:
        queryset = User.objects.all()
        list_allowed_methods = ['get']
        fields = ["username", "resource_uri"]

        authentication = MTApiKeyAuthentication()




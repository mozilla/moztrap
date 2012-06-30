from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import  Authorization
from tastypie.resources import ModelResource, ALL
from tastypie import fields

from .models import Product, ProductVersion, ApiKey
from ..environments.api import EnvironmentResource



class MTApiKeyAuthentication(ApiKeyAuthentication):
    """Authentication that requires our custom api key implementation."""

    def get_key(self, user, api_key):
        try:
            ApiKey.objects.get(owner=user, key=api_key, active=True)

        except:
            return self._unauthorized()

        return True


    def is_authenticated(self, request, **kwargs):
        """
        Finds the user and checks their API key.

        This overrides Tastypie's default impl, because we use a User
        proxy class, which Tastypie doesn't find

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        from .auth import User

        username = request.GET.get('username') or request.POST.get('username')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')

        if not username or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user
        return self.get_key(user, api_key)



class ReportResultsAuthorization(Authorization):
    """Authorization that only allows users with execute privileges."""

    def is_authorized(self, request, object=None):
        if request.user.has_perm("execution.execute"):
            return True
        else:
            return False



class ProductVersionResource(ModelResource):
    """
    Return a list of product versions.

    Filterable by version field.
    """

    class Meta:
        queryset = ProductVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "version", "codename"]
        filtering = {
            "version": ALL,
            }



class ProductResource(ModelResource):
    """
    Return a list of products.

    Filterable by name field.
    """

    productversions = fields.ToManyField(
        ProductVersionResource,
        "versions",
        full=True,
        )

    class Meta:
        queryset = Product.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name", "description"]
        filtering = {"name": ALL}



class ProductVersionEnvironmentsResource(ModelResource):
    """Return a list of productversions with full environment info."""

    environments = fields.ToManyField(
        EnvironmentResource,
        "environments",
        full=True,
        )

    class Meta:
        queryset = ProductVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "version", "codename"]


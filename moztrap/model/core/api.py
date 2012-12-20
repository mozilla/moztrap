from tastypie.authorization import  Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Product, ProductVersion, ApiKey
from ..environments.api import EnvironmentResource
from ..mtapi import MTResource, MTAuthorization, MTApiKeyAuthentication

import logging
logger = logging.getLogger(__name__)

class ReportResultsAuthorization(Authorization):
    """Authorization that only allows users with execute privileges."""

    def is_authorized(self, request, object=None):
        if request.method == "GET":
            return True
        elif request.user.has_perm("execution.execute"):
            return True
        else:
            return False



class ProductVersionResource(ModelResource):
    """
    Return a list of product versions.

    Filterable by version field.
    """
    product = fields.ToOneField("moztrap.model.core.api.ProductResource", "product")

    class Meta:
        queryset = ProductVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "version", "codename", "product"]
        filtering = {
            "version": ALL,
            "product": ALL_WITH_RELATIONS,
            }



class ProductResource(MTResource):
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
        list_allowed_methods = ["get", "post"]
        detail_allowed_methods = ["get", "put", "delete"]
        fields = ["id", "name", "description"]
        filtering = {"name": ALL}
        authentication = MTApiKeyAuthentication()
        authorization = MTAuthorization()
        always_return_data = True


    @property
    def model(self):
        """Model class related to this resource."""
        return Product


    # def obj_create(self, bundle, request=None, **kwargs):
    #     """Set the created_by field for the object to the request's user"""
    #     try:
    #         bundle = super(MTResource, self).obj_create(bundle=bundle, request=request, **kwargs)
    #         bundle.obj.created_by = request.user
    #         bundle.obj.save(user=request.user)
    #         return bundle
    #     except Exception as e:
    #         logger.debug("error creating %s" % e)


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


from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse

from .models import Product, ProductVersion
from .auth import User
from ..environments.api import EnvironmentResource
from ..mtapi import MTResource, MTAuthorization

import logging
logger = logging.getLogger(__name__)

class ReportResultsAuthorization(MTAuthorization):
    """Authorization that only allows users with execute privileges."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "execution.execute"



class ProductVersionAuthorization(MTAuthorization):
    """A permission of 'core.manage_productversions does not exist,
    use core.manage_products instead."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "core.manage_products"



class ProductVersionResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for Product Version.

    Filterable by version and product fields.
    """
    product = fields.ToOneField(
        "moztrap.model.core.api.ProductResource", "product")

    class Meta(MTResource.Meta):
        queryset = ProductVersion.objects.all()
        fields = ["id", "version", "codename", "product"]
        filtering = {
            "version": ALL,
            "product": ALL_WITH_RELATIONS,
            }
        authorization = ProductVersionAuthorization()
        ordering = ['product__id', 'version', 'id']


    @property
    def model(self):
        """Model class related to this resource."""
        return ProductVersion



class ProductResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for Product.

    Filterable by name field.
    """

    productversions = fields.ToManyField(
        ProductVersionResource,
        "versions",
        full=True,
        )

    class Meta(MTResource.Meta):
        queryset = Product.objects.all()
        fields = ["id", "name", "description"]
        filtering = {"name": ALL}
        ordering = ['name', 'id']


    @property
    def model(self):
        """Model class related to this resource."""
        return Product


    def obj_create(self, bundle, request=None, **kwargs):
        """Oversee the creation of product and its required productversion.
        Probably not strictly RESTful.
        """

        pv_required_msg = str("The 'productversions' key must exist, " +
                          "must be a list, and the list must contain " +
                          "at least one entry.")
        # pull the productversions off, they don't exist yet
        try:
            productversions = bundle.data.pop('productversions')
            if not isinstance(productversions, list):
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(pv_required_msg))
            if not len(productversions):
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(pv_required_msg))

            bundle.data["productversions"] = []
        except KeyError:
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest(pv_required_msg))

        # create the product
        updated_bundle = super(ProductResource, self).obj_create(
            bundle=bundle, request=request, **kwargs)

        # create the productversions
        for pv in productversions:
            ProductVersion.objects.get_or_create(
                product=updated_bundle.obj, **pv)

        return updated_bundle


    def obj_update(self, bundle, request=None, **kwargs):
        """Oversee updating of product.
        If this were RESTful, it would remove all existing versions and add
        the requested versions. But this isn't restful, it just adds the
        version if it doesn't exist already.
        """

        # pull the productversions off, you can't edit them from here
        productversions = bundle.data.pop("productversions", [])
        bundle.data["productversions"] = []

        updated_bundle =  super(ProductResource, self).obj_update(
            bundle=bundle, request=request, **kwargs)

        # create the productversions
        for pv in productversions:
            ProductVersion.objects.get_or_create(
                product=updated_bundle.obj, **pv)

        return updated_bundle



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



class UserResource(ModelResource):
    """Return a list of usernames"""

    class Meta:
        queryset = User.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "username"]


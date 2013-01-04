from tastypie import fields
from tastypie.resources import ALL

from .models import Tag
from ..mtapi import MTResource, MTAuthorization, MTApiKeyAuthentication
# from ..core.api import ProductResource

import logging
logger = logging.getLogger(__name__)



class TagResource(MTResource):


    # product = fields.ToOneField(
    #     ProductResource,
    #     "tag",
    #     full=False,
    #     )

    #XXX caseversions

    class Meta:
        queryset = Tag.objects.all()
        list_allowed_methods = ["get", "post"]
        detail_allowed_methods = ["get", "put", "delete"]
        fields = ["id", "name", "description", "product"]  #XXX caseversions
        filtering = {
            "name": ALL
            }
        authentication = MTApiKeyAuthentication()
        authorization = MTAuthorization()
        always_return_data = True

    @property
    def model(self):
        """Model class related to this resource."""
        return Tag




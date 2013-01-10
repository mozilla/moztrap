from tastypie import fields
from tastypie import http
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse

from .models import Tag
from ..mtapi import MTResource, MTAuthorization, MTApiKeyAuthentication
from ..core.api import ProductResource

import logging
logger = logging.getLogger(__name__)



class TagResource(MTResource):


    product = fields.ToOneField(
        ProductResource,
        "product",
        full=False,
        null=True,
        )

    #XXX caseversions

    class Meta:
        queryset = Tag.objects.all()
        list_allowed_methods = ["get", "post"]
        detail_allowed_methods = ["get", "put", "delete"]
        fields = ["id", "name", "description", "product"]  #XXX caseversions
        filtering = {
            "name": ALL,
            "product": ALL_WITH_RELATIONS,
            }
        authentication = MTApiKeyAuthentication()
        authorization = MTAuthorization()
        always_return_data = True

    @property
    def model(self):
        """Model class related to this resource."""
        return Tag


    def obj_update(self, bundle, request=None, **kwargs):
        """Lots of rules for modifying product for tags."""
        tag_id = bundle.request.path.split('/')[-2] # pull id out of path
        tag = self.model.objects.get(id=tag_id)
        caseversions = tag.caseversions.all()
        err_msg = "Tag's Product may not be changed unless the tag is not in use, the product is being set to None, or the product matches the existing cases."
        
        # if we're even thinking about changing the product
        if 'product' in bundle.data.keys():
            # if tag is in use
            if caseversions:
                desired_product = bundle.data['product']
                products = set([cv.productversion.product for cv in caseversions])
                # if desired product != current product
                if desired_product != tag.product:
                    # if desired product != None
                    if desired_product != None:  # coverage thinks there's a problem here, but i've seen it reach both logging statements
                        logger.debug('coverage 2')
                        # if existing caseversions represent more than one product
                        if len(products) > 1:
                            logger.exception(err_msg)
                            raise ImmediateHttpResponse(response=http.HttpBadRequest(err_msg))
                        elif str(list(products)[0].id) != desired_product.split('/')[-2]: # pull id out of uri
                            logger.exception(err_msg)
                            raise ImmediateHttpResponse(response=http.HttpBadRequest(err_msg))
                else: 
                    logger.debug('coverage 1')
        return super(TagResource, self).obj_update(bundle=bundle, request=request, **kwargs)


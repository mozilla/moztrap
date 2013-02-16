from tastypie import fields
from tastypie import http
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse

from .models import Tag
from ..mtapi import MTResource
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

    #@@@ additional relationship caseversions needs to be handled

    class Meta(MTResource.Meta):
        queryset = Tag.objects.all()
        fields = ["id", "name", "description", "product"]
        filtering = {
            "name": ALL,
            "product": ALL_WITH_RELATIONS,
            }
        ordering = ['name', 'product__id', 'id']

    @property
    def model(self):
        """Model class related to this resource."""
        return Tag


    def obj_update(self, bundle, request=None, **kwargs):
        """Lots of rules for modifying product for tags."""
        tag = self.get_via_uri(bundle.request.path, request)
        caseversions = tag.caseversions.all()
        err_msg = str("Tag's Product may not be changed unless " +
                  "the tag is not in use, the product is being " +
                  "set to None, or the product matches the existing cases.")

        # if we're even thinking about changing the product
        if 'product' in bundle.data.keys():
            logger.debug('thinking about product')
            # if tag is in use
            if caseversions:
                logger.debug('tag in use')
                desired_product = bundle.data['product']
                products = set(
                    [cv.productversion.product for cv in caseversions]
                    )
                # if it is *changing* the product
                if desired_product != tag.product:
                    logger.debug('changing product')
                    # if changing from global to product-specific
                    if not desired_product == None:
                        logger.debug('changing from global to product-specific')
                        # if existing caseversions represent more than one
                        # product
                        desired_product_id = self._id_from_uri(desired_product)
                        if len(products) > 1:
                            logger.exception(err_msg)
                            raise ImmediateHttpResponse(
                                response=http.HttpBadRequest(err_msg))
                        # or if cases' product is not requested product
                        elif str(list(products)[0].id) != desired_product_id:
                            logger.exception(err_msg)
                            raise ImmediateHttpResponse(
                                response=http.HttpBadRequest(err_msg))
        # code from here through the last else is optional,
        # but nice if tracking down coverage problems
                         # requested product matches the single product used by
                         # all of the caseversions
                        else:
                            logger.debug(
                                "product matches caseversions' product")
                    else:  # changing from product-specific to global
                        logger.debug("changing from product-specific to global")
                else:
                    logger.debug("not changing product")
            else:
                logger.debug("tag not in use")
        else:
            logger.debug("not thinking about product")

        return super(TagResource, self).obj_update(
            bundle=bundle, request=request, **kwargs)

from tastypie import fields
from tastypie import http
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse
from ..mtapi import MTResource, MTAuthorization

from .models import Profile, Environment, Element, Category

import logging
logger = logging.getLogger(__name__)


class EnvironmentAuthorization(MTAuthorization):
    """Atypically named permission."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "environments.manage_environments"



class ProfileResource(MTResource):
    """Create, Read, Update, and Delete capabilities for Profile."""

    class Meta(MTResource.Meta):
        queryset = Profile.objects.all()
        fields = ["id", "name"]
        authorization = EnvironmentAuthorization()
        ordering = ["id", "name"]
        filtering = {
            "name": ALL,
        }

    @property
    def model(self):
        """Model class related to this resource."""
        return Profile



class CategoryResource(MTResource):
    """Create, Read, Update and Delete capabilities for Category."""

    elements = fields.ToManyField(
        "moztrap.model.environments.api.ElementResource",
        "elements",
        full=True,
        readonly=True
    )

    class Meta(MTResource.Meta):
        queryset = Category.objects.all()
        fields = ["id", "name"]
        authorization = EnvironmentAuthorization()
        ordering = ["id", "name"]
        filtering = {
            "name": ALL,
        }


    @property
    def model(self):
        """Model class related to this resource."""
        return Category



class ElementResource(MTResource):
    """Create, Read, Update and Delete capabilities for Element."""

    category = fields.ForeignKey(CategoryResource, "category")

    class Meta(MTResource.Meta):
        queryset = Element.objects.all()
        fields = ["id", "name", "category"]
        authorization = EnvironmentAuthorization()
        filtering = {
            "category": ALL_WITH_RELATIONS,
            "name": ALL,
        }
        ordering = ["id", "name"]


    @property
    def model(self):
        """Model class related to this resource."""
        return Element


    @property
    def read_create_fields(self):
        """List of fields that are required for create
        but read-only for update."""
        return ["category"]



class EnvironmentResource(MTResource):
    """Create, Read and Delete capabilities for environments"""

    elements = fields.ToManyField(ElementResource, "elements")
    # an environment is not required to be associated with a profile
    profile = fields.ForeignKey(ProfileResource, "profile", null=True)

    class Meta(MTResource.Meta):
        queryset = Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'put', 'delete']
        fields = ["id", "profile", "elements"]
        filtering = {
            "elements": ALL,
            "profile": ALL_WITH_RELATIONS,
        }
        ordering = ["id", "profile"]


    @property
    def model(self):
        """Model class related to this resource."""
        return Environment


    def hydrate_m2m(self, bundle):
        """Validate the elements,
        which should each belong to separate categories."""

        bundle = super(EnvironmentResource, self).hydrate_m2m(bundle)
        elem_categories = [elem.data['category'] for elem in
                           bundle.data['elements']]
        if len(set(elem_categories)) != len(bundle.data['elements']):
            error_msg = "Elements must each belong to a different Category."
            logger.error(error_msg)
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest(error_msg))
        return bundle


    def patch_list(self, request, **kwargs):
        """
        Since there is no RESTful way to do what we want to do, and since
        ``PATCH`` is poorly defined with regards to RESTfulness, we are
        overloading ``PATCH`` to take a single request that performs
        combinatorics and creates multiple objects.
        """
        import itertools
        from django.db import transaction
        from tastypie.utils import dict_strip_unicode_keys

        deserialized = self.deserialize(
            request,
            request.raw_post_data,
            format=request.META.get('CONTENT_TYPE', 'application/json'))

        # verify input
        categories = deserialized.pop('categories', [])
        if not categories or not isinstance(categories, list):
            error_msg = "PATCH request must contain categories list."
            logger.error(error_msg)
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest(error_msg))


        # do the combinatorics
        elem_lists = []
        for cat in categories:
            # do some type validation / variation
            if isinstance(cat, basestring):
                # simple case of create all the combinations
                cat = Category.objects.filter(id=self._id_from_uri(cat))
                elem_list = Element.objects.filter(category=cat)
            elif isinstance(cat, dict):
                # we must be working with at least one partial category
                category = Category.objects.filter(
                    id=self._id_from_uri(cat['category']))
                elem_list = Element.objects.filter(category=category)
                if 'exclude' in cat:
                    # exclude some element(s) from the combinations
                    exclude_uris = cat['exclude']
                    exclude_ids = [int(
                        self._id_from_uri(x)) for x in exclude_uris]
                    elem_list = [elem for elem in elem_list
                                 if elem.id not in exclude_ids]
                elif 'include' in cat:
                    # include only a few elements in the combinations
                    include_uris = cat['include']
                    include_ids = [int(
                        self._id_from_uri(x)) for x in include_uris]
                    elem_list = [elem for elem in elem_list
                                 if elem.id in include_ids]
                else:
                    # don't worry about this,
                    # it'll act like a list of categories
                    pass  # pragma: no cover
            else:
                error_msg = "categories list must contain resource uris or hashes."
                logger.error(error_msg)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_msg))

            # save off the elements from this category that will be used
            elem_lists.append(elem_list)

        # create all the combinations of elements from categories
        combinatorics = itertools.product(*elem_lists)

        # do the creation
        with transaction.commit_on_success():
            for combo in combinatorics:
                deserialized['elements'] = combo
                bundle = self.build_bundle(
                    data=dict_strip_unicode_keys(deserialized))
                bundle.request.META['REQUEST_METHOD'] = 'PATCH'
                self.is_valid(bundle, request)
                self.obj_create(bundle, request=request)

        # don't try to reply with data, the request doesn't
        # really match the results.
        return http.HttpAccepted()

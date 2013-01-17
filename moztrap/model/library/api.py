import datetime
from tastypie.exceptions import BadRequest

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from ..core.api import (ProductVersionResource, ProductResource,
                        UserResource)
from .models import CaseVersion, Case, Suite, CaseStep
from ..mtapi import MTResource
from ..environments.api import EnvironmentResource
from ..tags.api import TagResource


class SuiteResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for Suite.

    Filterable by name and product fields.
    """

    product = fields.ToOneField(ProductResource, "product")

    class Meta(MTResource.Meta):
        queryset = Suite.objects.all()
        fields = ["name", "product", "description", "status", "id"]
        filtering = {
            "name": ALL,
            "product": ALL_WITH_RELATIONS,
            }
        ordering = ['name', 'product__id', 'id']

    @property
    def model(self):
        """Model class related to this resource."""
        return Suite



class CaseResource(ModelResource):
    suites = fields.ToManyField(SuiteResource, "suites", full=True)

    class Meta:
        queryset = Case.objects.all()
        fields= ["id", "suites"]
        filtering = {
            "suites": ALL_WITH_RELATIONS,
            }



class CaseStepResource(ModelResource):


    class Meta:
        queryset = CaseStep.objects.all()
        fields = ["instruction", "expected"]



class CaseVersionResource(ModelResource):

    case = fields.ForeignKey(CaseResource, "case", full=True)
    steps = fields.ToManyField(CaseStepResource, "steps", full=True)
    environments = fields.ToManyField(
        EnvironmentResource, "environments", full=True)
    productversion = fields.ForeignKey(
        ProductVersionResource, "productversion")
    tags = fields.ToManyField(TagResource, "tags", full=True)


    class Meta:
        queryset = CaseVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name", "description", "case"]
        filtering = {
            "environments": ALL,
            "productversion": ALL_WITH_RELATIONS,
            "case": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            }



class BaseSelectionResource(ModelResource):
    """Adds filtering by negation for use with multi-select widget"""
    #@@@ move this to mtapi.py when that code is merged in.

    def apply_filters(self,
        request, applicable_filters, applicable_excludes={}):
        """Apply included and excluded filters to query."""
        return self.get_object_list(request).filter(
            **applicable_filters).exclude(**applicable_excludes)


    def obj_get_list(self, request=None, **kwargs):
        """Return the list with included and excluded filters, if they exist."""
        filters = {}

        if hasattr(request, 'GET'): # pragma: no cover
            # Grab a mutable copy.
            filters = request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)

        # Splitting out filtering and excluding items
        new_filters = {}
        excludes = {}
        for key, value in filters.items():
            # If the given key is filtered by ``not equal`` token, exclude it
            if key.endswith('__ne'):
                key = key[:-4] # Stripping out trailing ``__ne``
                excludes[key] = value
            else:
                new_filters[key] = value

        filters = new_filters

        # Building filters
        applicable_filters = self.build_filters(filters=filters)
        applicable_excludes = self.build_filters(filters=excludes)

        base_object_list = self.apply_filters(
            request, applicable_filters, applicable_excludes)
        return self.apply_authorization_limits(request, base_object_list)



class CaseSelectionResource(BaseSelectionResource):
    """
    Specialty end-point for an AJAX call in the Suite form multi-select widget
    for selecting cases.
    """

    case = fields.ForeignKey(CaseResource, "case")
    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
    tags = fields.ToManyField(TagResource, "tags", full=True)
    created_by = fields.ForeignKey(UserResource, "created_by", full=True, null=True)

    class Meta:
        queryset = CaseVersion.objects.all().select_related(
            "case",
            "productversion",
            "created_by",
            ).prefetch_related(
                "tags",
                "case__suitecases",
                ).distinct().order_by("case__suitecases__order")
        list_allowed_methods = ['get']
        fields = ["id", "name", "latest", "created_by"]
        filtering = {
            "productversion": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            "case": ALL_WITH_RELATIONS,
            "latest": ALL,
            "created_by": ALL_WITH_RELATIONS
            }


    def dehydrate(self, bundle):
        """Add some convenience fields to the return JSON."""

        case = bundle.obj.case
        bundle.data["case_id"] = unicode(case.id)
        bundle.data["product_id"] = unicode(case.product_id)
        bundle.data["product"] = {"id": unicode(case.product_id)}

        if "case__suites" in bundle.request.GET.keys():
            suite_id=int(bundle.request.GET["case__suites"])
            order = [x.order for x in case.suitecases.all()
                if x.suite_id == suite_id][0]
            bundle.data["order"] = order
        else:
            bundle.data["order"] = None

        return bundle



class CaseVersionSelectionResource(BaseSelectionResource):
    """
    Specialty end-point for an AJAX call in the Tag form multi-select widget
    for selecting caseversions.
    """

    case = fields.ForeignKey(CaseResource, "case")
    productversion = fields.ForeignKey(
        ProductVersionResource, "productversion", full=True)
    tags = fields.ToManyField(TagResource, "tags", full=True)
    created_by = fields.ForeignKey(UserResource, "created_by", full=True, null=True)

    class Meta:
        queryset = CaseVersion.objects.all().select_related(
            "case",
            "productversion",
            "created_by",
            ).prefetch_related(
            "tags",
            )
        list_allowed_methods = ['get']
        fields = ["id", "name", "latest", "created_by_id"]
        filtering = {
            "productversion": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            "case": ALL_WITH_RELATIONS,
            "created_by": ALL_WITH_RELATIONS
            }


    def dehydrate(self, bundle):
        """Add some convenience fields to the return JSON."""

        case = bundle.obj.case
        bundle.data["case_id"] = unicode(case.id)
        bundle.data["product_id"] = unicode(case.product_id)
        bundle.data["product"] = {"id": unicode(case.product_id)}
        bundle.data["productversion_name"] = bundle.obj.productversion.name

        return bundle

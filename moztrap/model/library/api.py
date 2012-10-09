from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.resources import ModelResource

from .models import CaseVersion, Case, Suite, CaseStep, SuiteCase
from ..environments.api import EnvironmentResource
from ..core.api import ProductVersionResource
from ..tags.api import TagResource


class SuiteResource(ModelResource):


    class Meta:
        queryset = Suite.objects.all()
        fields = ["name"]
        filtering = {
            "name": ALL,
            }



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
    environments = fields.ToManyField(EnvironmentResource, "environments", full=True)
    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
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




class SuiteCaseSelectionResource(ModelResource):
    """
    Specialty end-point for an AJAX call in the Suite form multi-select widget
    for selecting cases.
    """

    case = fields.ForeignKey(CaseResource, "case")
    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
    tags = fields.ToManyField(TagResource, "tags", full=True)

    class Meta:
        queryset = CaseVersion.objects.filter(latest=True).select_related(
            "case",
            "productversion",
            )
        # @@@ Django 1.4 - use prefetch_related on the tag field
        list_allowed_methods = ['get']
        fields = ["id", "name"]
        filtering = {
            "productversion": ALL_WITH_RELATIONS,
            }

    def dehydrate(self, bundle):
        """Add some convenience fields to the return JSON."""

        case = bundle.obj.case
        bundle.data["case_id"] = case.id
        bundle.data["created_by"] = case.created_by
        order = None
        try:
            if hasattr(bundle.request.GET, "for_suite"):
                order = case.suitecases.get(
                    suite__id=bundle.request.GET["for_suite"]
                    ).order
        except SuiteCase.DoesNotExist:
            pass

        bundle.data["order"] = order

        return bundle


    def alter_list_data_to_serialize(self, request, data):
        """Split list of cases between included and excluded from the suite"""
        included = [x for x in data["objects"] if x.data["order"] is not None]
        included = sorted(included, key=lambda k: k.data["order"])
        excluded =  [x for x in data["objects"] if x.data["order"] is None]
        data["objects"] = {"sel": included, "unsel": excluded}
        return data
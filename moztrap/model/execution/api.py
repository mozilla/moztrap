from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Run, RunCaseVersion, Result
from ..core.api import ProductVersionResource

from ..environments.models import Environment



# /run/
class RunResource(ModelResource):
    """ Fetch the test runs for the specified product and version. """
    productversion = fields.ForeignKey(ProductVersionResource, "productversion")

    class Meta:
        queryset = Run.objects.all()
        fields = [
            "id",
            "name",
            "description",
            "resource_uri",
            "status",
            "productversion",
            ]
        filtering = {
            "productversion": (ALL_WITH_RELATIONS),
            "product_version_name": ("exact"),
            "status": ("exact"),
        }

    def dehydrate(self, bundle):
        pv = bundle.obj.productversion
        bundle.data['productversion_name'] = pv.version
        bundle.data['product_name'] = pv.product.name

        return bundle

# /run/<id>/cases
class RunCasesResource(RunResource):
    """ Fetch a test run with all its associated cases. """

    def dehydrate(self, bundle):
        bundle = super(RunCasesResource, self).dehydrate(bundle)

        # get cases for this run
        caseversions = bundle.obj.caseversions.all()
        cases = []
        for caseversion in caseversions:
            case = caseversion.case
            prefix_dash_id = "{0}-{1}".format(
                case.idprefix,
                case.id,
                ) if not case.idprefix == "" else case.id

            cases.append({
                "id": case.id,
                "prefix_id": prefix_dash_id,
                "name": caseversion.name,
                "description": caseversion.description,
            })
        bundle.data["cases"] = cases

        return bundle


# run/<id>/environments
class RunEnvironmentsResource(RunResource):
    """Fetch a test run with all its associated environments"""

    def dehydrate(self, bundle):
        bundle = super(RunEnvironmentsResource, self).dehydrate(bundle)

        environments = bundle.obj.environments.all()
        runenvs = []
        for env in environments:
            runenvs.append({
                "id": env.id,
                "environment": [x.name for x in env.elements.all()],
            })

        bundle.data["environments"] = runenvs
        return bundle

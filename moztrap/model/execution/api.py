from tastypie.resources import ModelResource
from tastypie import fields

from .models import Run, RunCaseVersion, Result
from ..environments.models import Environment



# /run/
class RunResource(ModelResource):
    """
    Fetch the test runs for the specified product and version
    """
#    caseversions = fields.ToManyField(
#        RunCaseVersionResource,
#        'runcaseversions',
#        )

    class Meta:
        queryset = Run.objects.all()
        fields = ["id", "name", "description", "resource_uri"]


# /run/<id>/cases
class RunCasesResource(ModelResource):
    """
    Fetch the cases for the specified test run

    """
#    caseversions = fields.ToManyField(
#        RunCaseVersionResource,
#        'runcaseversions',
#        full=True,
#        )

    class Meta:
        queryset = Run.objects.all()
        fields = ["id", "name", "description", "resource_uri"]


    def dehydrate(self, bundle):
        productversion_version = bundle.obj.productversion.version
        bundle.data['productversion_version'] = productversion_version
        product_name = bundle.obj.productversion.product.name
        bundle.data['product_name'] = product_name

        # get cases for this run
        caseversions = bundle.obj.caseversions.all()
        cases = []
        for caseversion in caseversions:
            case = caseversion.case
            cases.append({
                "id": case.id,
                "prefix_id": "{0}-{1}".format(case.idprefix, case.id) if not case.idprefix == "" else case.id,
                "name": caseversion.name,
                "description": caseversion.description,
            })
        bundle.data["cases"] = cases

        return bundle


# run/<id>/environments
class RunEnvironmentsResource(ModelResource):
#    environments = fields.ToManyField(
#        EnvironmentResource,
#        "environments",
#    )

    class Meta:
        queryset = Environment.objects.all()


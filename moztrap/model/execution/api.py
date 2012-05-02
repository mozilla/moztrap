from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication

from json import loads

from .models import Run, RunCaseVersion, Result
from ..core.api import ProductVersionResource
from ..core.auth import User

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
    """
    Fetch a test run with all its associated cases.

    @@@ - This is returning just the caseversions, but not possibly associated
    results.  Would we want to return any existing results for the caseversion/
    env/user combo, too?  So that the client could see that some already
    existed?  For automation, that may not matter but if someone used this in
    some other type of client tool, they likely would so they don't repeat
    existing tests.
    """

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

class ResultsResource(ModelResource):

    class Meta:

        queryset = Results.objects.all()
        resource_name = 'results'
        list_allowed_methods = ['post']
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()

    def post_list(self, request, **kwargs):
        """
        Create the new Resource object for the caseversions and environments
        provided in each Result object of the JSON.

        It's possible that the result already exists for this user/caseversion/
        env combination.  So in that case we would want to update that result.
        """
        result_list = loads(request.data)

        for item in result_list:
            result, created = Result.objects.get_or_create(
#                user=request.user,
                user = User.objects.get(username="camd"),
                environment__id=item["environment_id"],
                runcaseversion__caseversion__id=item["caseversion_id"],
                )
            result.status = item.status
            result.comment = item.comment
            #@@@ - support bug_url
            result.save()


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

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication

from json import loads

from .models import Run, RunCaseVersion, Result, StepResult
from ..core.api import ProductVersionResource, UserResource
from ..core.auth import User
from ..environments.api import EnvironmentResource
from ..library.api import CaseVersionResource



# /run/
class RunResource(ModelResource):
    """ Fetch the test runs for the specified product and version. """

    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
    environments = fields.ToManyField(EnvironmentResource, "environments")

    class Meta:
        queryset = Run.objects.all()
        fields = [
            "id",
            "name",
            "description",
            "resource_uri",
            "status",
            "productversion",
            "environments",
            "runcaseversions",
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



class RunCaseVersionResource(ModelResource):
    run = fields.ForeignKey(RunResource, "run")
    caseversion = fields.ForeignKey(CaseVersionResource, "caseversion", full=True)

    class Meta:
        queryset = RunCaseVersion.objects.all()
        filtering = {
            "run": (ALL_WITH_RELATIONS),
            }
        fields = {"id", "resource_uri"}



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



class StepResultResource(ModelResource):

    class Meta:
        queryset = StepResult.objects.all()
        fields = {
            "bug_url",
            "status",
            "resource_uri",
            }



class ResultResource(ModelResource):
    environment = fields.ForeignKey(EnvironmentResource, "environment", full=True)
    runcaseversion = fields.ForeignKey(RunCaseVersionResource, "runcaseversion", full=True)
    tester = fields.ForeignKey(UserResource, "tester", full=True)
    stepresults = fields.ToManyField(StepResultResource, "stepresults", full=True)

    class Meta:

        queryset = Result.objects.all()
        resource_name = 'result'
        #list_allowed_methods = ['put']
        authentication = Authentication()
        authorization = Authorization()
#        authentication = ApiKeyAuthentication()
#        authorization = DjangoAuthorization()

        filtering = {
            "runcaseversion": (ALL_WITH_RELATIONS),
            "environment": (ALL),
            }
        fields = {
            "id",
            "resource_uri",
            "runcaseversion",
            "environment",
            "status",
            "tester",
            "comment",
            "stepresults"
            }

    # I don't think I need this.  should be able to just POST the data.
    def x_put_list(self, request, **kwargs):
        """
        Create the new Resource object for the caseversions and environments
        provided in each Result object of the JSON.

        It's possible that the result already exists for this user/caseversion/
        env combination.  So in that case we would want to update that result.

        """
#        assert False, request.raw_post_data
        result_list = loads(request.PUT.values()[0])

        run_id = request.GET.get("run_id")

        for item in result_list:
            rcv = RunCaseVersion.objects.get(run=run_id, caseversion=caseversion_id)

            result, created = Result.objects.get_or_create(
#                user=request.user,
#                tester = request.user,
                runcaseversion=rcv,
                user = User.objects.get(username="camd"),
                environment__id=item["environment_id"],
                )

            # just call method on result to set status instead
            assert False
            result.status = item.status
            result.comment = item.comment

            #@@@ - support bug_url
            result.save()



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

"""
Authentication:  use API Key.
    In short term, we create an API key for every user, and they have to ask the admin for that key.
    the admin gets it in the admin console.
    admin goes to the user management page a button to generate api key and copy and email it to the user.

Authorization: need custom class

"""
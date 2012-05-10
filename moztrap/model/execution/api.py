from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication

from ..mtresource import MTModelResource
from .models import Run, RunCaseVersion, Result, StepResult
from ..environments.models import Environment
from ..core.api import ProductVersionResource, UserResource
from ..core.auth import User
from ..environments.api import EnvironmentResource
from ..library.api import CaseVersionResource



class RunResource(MTModelResource):
    """ Fetch the test runs for the specified product and version. """

    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
#    environments = fields.ToManyField(EnvironmentResource, "environments")

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
            "status": ("exact"),
        }

    def dehydrate(self, bundle):
        pv = bundle.obj.productversion
        bundle.data['productversion_name'] = pv.version
        bundle.data['product_name'] = pv.product.name

        return bundle



class RunEnvironmentsResource(RunResource):
    """Fetch a test run with all its associated environments"""

    environments = fields.ToManyField(EnvironmentResource, "environments", full=True)

    class Meta:
        queryset = Run.objects.all()
        fields = [
            "id",
            "name",
            "description",
            "resource_uri",
            "status",
            "environments",
            ]



class RunCaseVersionResource(ModelResource):
    """
    RunCaseVersion represents the connection between a run and a caseversion.

    It is possible to return a result for each runcaseversion.  So the result
    will sit as a peer to the caseversion under the runcaseversion.

    How do I post this, then?  Not this this url.  presumably with the results URL,
    but I will need to have a link to the appropriate runcaseversion within each Result as a ForeignKey?

    """

    run = fields.ForeignKey(RunResource, "run")
    caseversion = fields.ForeignKey(CaseVersionResource, "caseversion", full=True)

    class Meta:
        queryset = RunCaseVersion.objects.all()
        filtering = {
            "run": (ALL_WITH_RELATIONS),
            "caseversion": (ALL_WITH_RELATIONS),
            }
        fields = {"id", "run", "run_id"}


    def dehydrate(self, bundle):

        # give the id of the run for convenience
        bundle.data["run_id"] = bundle.obj.run.id
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
    environment = fields.ForeignKey(EnvironmentResource, "environment")
    runcaseversion = fields.ForeignKey(RunCaseVersionResource, "runcaseversion")
    tester = fields.ForeignKey(UserResource, "tester")
    stepresults = fields.ToManyField(StepResultResource, "stepresults", full=True)

    class Meta:

        queryset = Result.objects.all()
        resource_name = 'result'
        list_allowed_methods = ['patch']
        authentication = Authentication()
        authorization = Authorization()
#        authentication = ApiKeyAuthentication()
#        authorization = DjangoAuthorization()


    def obj_create(self, bundle, request=None, **kwargs):
        """
        This is where I need to do the creation of the results objects myself.  I should call
        the set status field to "do the right things" like I talked about with Carl.

        """
#        return super(ResultResource, self).obj_create(bundle, request, **kwargs)

        data = bundle.data.copy()

        rcv = RunCaseVersion.objects.get(pk=data.pop("runcaseversion"))
        env = Environment.objects.get(pk=data.pop("environment"))
        tester = User.objects.get(pk=data.pop("tester"))
        user = User.objects.get(username=request.GET.get("username"))

        data["user"] = user

        result = Result(
            runcaseversion=rcv,
            environment=env,
            tester=tester,
            created_by=user,
        )
        result.save()

        status_methods = {
            "passed": result.finishsucceed,
            "failed": result.finishfail,
            "invalidated": result.finishinvalidate,
            }

        set_status = status_methods[data.pop("status")]
        set_status(**data)

        bundle.obj = result
        return bundle






"""
Authentication:  use API Key.
    In short term, we create an API key for every user, and they have to ask the admin for that key.
    the admin gets it in the admin console.
    admin goes to the user management page a button to generate api key and copy and email it to the user.

Authorization: need custom class

"""
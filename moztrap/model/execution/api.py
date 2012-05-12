from django.core.exceptions import ValidationError

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Run, RunCaseVersion, Result
from ..core.api import (ProductVersionResource, UserResource,
                        ReportResultsAuthorization, MTApiKeyAuthentication)
from ..core.auth import User
from ..environments.api import EnvironmentResource
from ..environments.models import Environment
from ..library.api import CaseVersionResource



class RunResource(ModelResource):
    """ Fetch the test runs for the specified product and version. """

    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
    environments = fields.ToManyField(EnvironmentResource, "environments", full=True)

    class Meta:
        queryset = Run.objects.all()
        list_allowed_methods = ['get']
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
            "productversion": ALL_WITH_RELATIONS,
            "status": "exact",
        }

    def dehydrate(self, bundle):
        pv = bundle.obj.productversion
        bundle.data['productversion_name'] = pv.version
        bundle.data['product_name'] = pv.product.name

        return bundle

    #TODO @@@ Cookbook for Tastypie
    """
    Cookbook item for Tastypie docs.
    Want full=false in the list endpoint and full=True in
    the detail endpoint
    """
    def dispatch_detail(self, request, **kwargs):
        """For details, we want the full info on environments for the run """
        self.fields["environments"].full=True
        return super(RunResource, self).dispatch_detail(request, **kwargs)


    def dispatch_list(self, request, **kwargs):
        """For list, we don't want the full info on environments """
        self.fields["environments"].full=False
        return super(RunResource, self).dispatch_list(request, **kwargs)



class RunCaseVersionResource(ModelResource):
    """
    RunCaseVersion represents the connection between a run and a caseversion.

    It is possible to return a result for each runcaseversion.  So the result
    will sit as a peer to the caseversion under the runcaseversion.

    """

    run = fields.ForeignKey(RunResource, "run")
    caseversion = fields.ForeignKey(CaseVersionResource, "caseversion", full=True)

    class Meta:
        queryset = RunCaseVersion.objects.all()
        list_allowed_methods = ['get']
        filtering = {
            "run": ALL_WITH_RELATIONS,
            "caseversion": ALL_WITH_RELATIONS,
            }
        fields = {"id", "run", "run_id"}


    def dehydrate(self, bundle):

        # give the id of the run for convenience
        bundle.data["run_id"] = str(bundle.obj.run.id)
        return bundle



class ResultResource(ModelResource):
    """
    Endpoint for submitting results for a set of runcaseversions.

    This endpoint is write only.  The submitted result objects should
    be formed like this::

        [
            {
                "environment": 1,
                "status": "passed",
                "tester": 1,
                "runcaseversion": 2
            },
            {
                "status": "failed",
                "comment": "why u no pass?",
                "tester": 1,
                "environment": 1,
                "runcaseversion": 19,
                "bug": "https://bugzilla.mycompany.com/show_bug.cgi?id=3502",
                "stepnumber": 1
            }
        ]

    """

    class Meta:
        queryset = Result.objects.all()
        resource_name = "result"
        list_allowed_methods = ["patch"]

        authentication = MTApiKeyAuthentication()
        authorization = ReportResultsAuthorization()


    def obj_create(self, bundle, request=None, **kwargs):
        """
        Manually create the proper results objects.

        This is necessary because we have special handler methods for
        setting the statuses which we want to keep DRY.

        """

        data = bundle.data.copy()

        try:
            rcv = RunCaseVersion.objects.get(pk=data.pop("runcaseversion"))
            env = Environment.objects.get(pk=data.pop("environment"))
            tester = User.objects.get(pk=data.pop("tester"))
            status = data.pop("status")

        except Exception as e:
            raise ValidationError(
                "bad result object data missing key: {0}".format(e))

        user = User.objects.get(username=request.user.username)
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

        set_status = status_methods[status]
        set_status(**data)

        bundle.obj = result
        return bundle

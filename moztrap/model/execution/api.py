from django.core.exceptions import ValidationError

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import Run, RunCaseVersion, Result
from ..core.api import (ProductVersionResource, UserResource,
                        ReportResultsAuthorization, MTApiKeyAuthentication)
from ..core.auth import User
from ..core.models import ProductVersion
from ..environments.api import EnvironmentResource
from ..environments.models import Environment
from ..library.api import CaseVersionResource
from ..library.models import CaseVersion



class RunCaseVersionResource(ModelResource):
    """
    RunCaseVersion represents the connection between a run and a caseversion.

    It is possible to return a result for each runcaseversion.  So the result
    will sit as a peer to the caseversion under the runcaseversion.

    """

    run = fields.ToOneField(
        "moztrap.model.execution.api.RunResource",
        "run",
        related_name="runcaseversion")
    caseversion = fields.ToOneField(CaseVersionResource, "caseversion", full=True)

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




class RunResource(ModelResource):
    """
    Fetch the test runs for the specified product and version.

    It is also possible to create a new testrun as a copy of an existing one.
    """

    productversion = fields.ForeignKey(ProductVersionResource, "productversion")
    environments = fields.ToManyField(
        EnvironmentResource,
        "environments",
        full=False,
        )
    runcaseversions = fields.ToManyField(
        RunCaseVersionResource,
        "runcaseversions",
        )

    class Meta:
        queryset = Run.objects.all()
        list_allowed_methods = ["get", "post"]
        fields = [
            "id",
            "name",
            "description",
            "status",
            "productversion",
            "environments",
            "runcaseversions",
            ]
        filtering = {
            "productversion": ALL_WITH_RELATIONS,
            "status": "exact",
        }
        authentication = MTApiKeyAuthentication()
        authorization = ReportResultsAuthorization()


    def dehydrate(self, bundle):
        pv = bundle.obj.productversion
        bundle.data["productversion_name"] = pv.version
        bundle.data["product_name"] = pv.product.name

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


    def obj_create(self, bundle, request=None, **kwargs):
        """Set the created_by field for the run to the request's user"""

        bundle = super(RunResource, self).obj_create(bundle=bundle, request=request, **kwargs)
        user = User.objects.get(username=bundle.request.user.username)
        bundle.obj.created_by = user
        bundle.obj.save()
        return bundle


    def hydrate_runcaseversions(self, bundle):

        """
        Manually create the test run based on results objects.

        This is necessary because we have special handler methods for
        setting the statuses which we want to keep DRY.

        """

        try:
            run = bundle.obj
            run.save()

            # walk results

            for result in bundle.data["runcaseversions"]:

                # find caseversion for case
                cv = CaseVersion.objects.get(
                    productversion=run.productversion,
                    case=result.pop("case"),
                    )

                # create runcaseversion for this run to caseversion
                rcv, created = RunCaseVersion.objects.get_or_create(
                    run=run,
                    caseversion=cv,
                    )


                user = User.objects.get(username=bundle.request.user.username)
                result["user"] = user
                result["tester"] = user
                result["environment"] = Environment.objects.get(
                    pk=result["environment"])

                # create result via methods on runcaseversion
                rcv.create_result(**result)


            #TODO @@@ Cookbook for Tastypie
            #don't act on the data in here, we already did.  So emptying it.
            bundle.data["runcaseversions"] = []
            return bundle

        except Exception as e:
            raise ValidationError(
                "bad result object data missing key: {0}".format(e))





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
            case=data.pop("case")
            env = Environment.objects.get(pk=data.get("environment"))
            data["environment"] = env
            run=data.pop("run_id")

            rcv = RunCaseVersion.objects.get(
                run=run,
                caseversion__case__id=case,
                environments=env,
                )

        except Exception as e:
            raise ValidationError(
                "bad result object data missing key: {0}".format(e))

        user = User.objects.get(username=request.user.username)
        data["user"] = user
        data["tester"] = user

        bundle.obj = rcv.create_result(**data)
        return bundle

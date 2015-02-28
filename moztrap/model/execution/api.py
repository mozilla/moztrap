from django.db.models import Count
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie import http, fields
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.bundle import Bundle

import json

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse

from .models import Run, RunCaseVersion, RunSuite, Result
from ..mtapi import MTResource, MTApiKeyAuthentication, MTAuthorization
from ..core.api import (ProductVersionResource, ProductResource,
                        ReportResultsAuthorization, UserResource)
from ..environments.api import EnvironmentResource
from ..environments.models import Environment
from ..library.api import (CaseVersionResource, BaseSelectionResource,
                           SuiteResource)
from ..library.models import CaseVersion, Suite

from ...view.lists.filters import filter_url

import logging
logger = logging.getLogger(__name__)


class RunSuiteAuthorization(MTAuthorization):
    """Atypically named permission."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "execution.manage_runs"


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
        fields = ["id", "run"]



class RunResource(ModelResource):
    """
    Fetch the test runs for the specified product and version.

    It is also possible to create a new testrun, when posted.

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
        always_return_data = True


    def dehydrate(self, bundle):
        """Add some convenience fields to the return JSON."""

        pv = bundle.obj.productversion
        bundle.data["productversion_name"] = pv.version
        bundle.data["product_name"] = pv.product.name

        return bundle


    def dispatch_detail(self, request, **kwargs):
        """For details, we want the full info on environments for the run """

        self.fields["environments"].full = True
        return super(RunResource, self).dispatch_detail(request, **kwargs)


    def dispatch_list(self, request, **kwargs):
        """For list, we don't want the full info on environments """

        self.fields["environments"].full = False
        return super(RunResource, self).dispatch_list(request, **kwargs)


    def create_response(self, request, data,
                        response_class=HttpResponse, **response_kwargs):
        """On posting a run, return a url to the MozTrap UI for that new run."""

        resp = super(RunResource, self).create_response(
            request,
            data,
            response_class=response_class,
            **response_kwargs
            )

        if isinstance(data, Bundle):
            # data will be a bundle if we are creating a new Run.  And in that
            # case we want to add a URI to viewing this new run result in the UI
            full_url = filter_url(
                "results_runcaseversions",
                Run.objects.get(pk=data.data["id"]),
                )

            new_content = json.loads(resp.content)
            new_content["ui_uri"] = full_url
            new_content["resource_uri"] = data.data["resource_uri"]

            resp.content = json.dumps(new_content)
            # need to set the content type to application/json
            resp._headers["content-type"] = ("Content-Type", "application/json; charset=utf-8")
        return resp


    def obj_create(self, bundle, request=None, **kwargs):
        """Set the created_by field for the run to the request's user"""
        request = request or bundle.request
        bundle = super(RunResource, self).obj_create(bundle=bundle, request=request, **kwargs)
        bundle.obj.created_by = request.user
        bundle.obj.save()
        return bundle


    def hydrate_runcaseversions(self, bundle):
        """
        Handle the runcaseversion creation during a POST of a new Run.

        Tastypie handles the creation of the run itself.  But we handle the
        RunCaseVersions and Results because we have special handler methods for
        setting the statuses which we want to keep DRY.

        """

        try:
            run = bundle.obj
            run.save()

            # walk results

            for data in bundle.data["runcaseversions"]:

                status = data.pop("status")

                # find caseversion for case
                cv = CaseVersion.objects.get(
                    productversion=run.productversion,
                    case=data.pop("case"),
                    )

                # create runcaseversion for this run to caseversion
                rcv, created = RunCaseVersion.objects.get_or_create(
                    run=run,
                    caseversion=cv,
                    )


                data["user"] = bundle.request.user
                data["environment"] = Environment.objects.get(
                    pk=data["environment"])

                # create result via methods on runcaseversion
                rcv.get_result_method(status)(**data)

            bundle.data["runcaseversions"] = []
            return bundle

        except KeyError as e:
            raise ValidationError(
                "bad result object data missing key: {0}".format(e))

        except ObjectDoesNotExist as e:
            raise ValidationError(e)



class ResultResource(ModelResource):
    """
    Endpoint for submitting results for a set of runcaseversions.

    This endpoint is write only.  The submitted result objects should
    be formed like this::

        {
            "objects": [
                {
                    "case": "1",
                    "environment": "23",
                    "run_id": "1",
                    "status": "passed"
                },
                {
                    "case": "14",
                    "comment": "why u no make sense??",
                    "environment": "23",
                    "run_id": "1",
                    "status": "invalidated"
                },
                {
                    "bug": "http://www.deathvalleydogs.com",
                    "case": "326",
                    "comment": "why u no pass?",
                    "environment": "23",
                    "run_id": "1",
                    "status": "failed",
                    "stepnumber": 1
                }
            ]
        }

    """

    class Meta:
        queryset = Result.objects.all()
        resource_name = "result"
        list_allowed_methods = ["get", "patch"]

        filtering = {
            "created_on": ALL_WITH_RELATIONS,
        }

        authentication = MTApiKeyAuthentication()
        authorization = ReportResultsAuthorization()


    def obj_create(self, bundle, request=None, **kwargs):
        """
        Manually create the proper results objects.

        This is necessary because we have special handler methods in
        RunCaseVersion for setting the statuses which we want to keep DRY.

        """
        request = request or bundle.request
        data = bundle.data.copy()

        try:
            status = data.pop("status")
            case = data.pop("case")
            env = Environment.objects.get(pk=data.get("environment"))
            run = data.pop("run_id")

        except KeyError as e:
            raise ValidationError(
                "bad result object data missing key: {0}".format(e))

        except Environment.DoesNotExist as e:
            raise ValidationError(
                "Specified environment does not exist: {0}".format(e))


        data["environment"] = env

        try:
            rcv = RunCaseVersion.objects.get(
                run__id=run,
                caseversion__case__id=case,
                environments=env,
                )

        except RunCaseVersion.DoesNotExist as e:
            raise ValidationError(
                "RunCaseVersion not found for run: {0}, case: {1}, environment: {2}:\nError {3}".format(
                        str(run), str(case), str(env), e))

        self.authorized_create_detail([rcv], bundle)
        data["user"] = request.user

        method = rcv.get_result_method(status)
        bundle.obj = method(**data)
        return bundle



class RunSuiteResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for RunSuite.

    Filterable by suite and run fields.
    """

    run = fields.ForeignKey(RunResource, 'run')
    suite = fields.ForeignKey(SuiteResource, 'suite')

    class Meta(MTResource.Meta):
        queryset = RunSuite.objects.all()
        fields = ["suite", "run", "order", "id"]
        filtering = {
            "suite": ALL_WITH_RELATIONS,
            "run": ALL_WITH_RELATIONS
        }
        authorization = RunSuiteAuthorization()

    @property
    def model(self):
        return RunSuite


    @property
    def read_create_fields(self):
        """run and suite are read-only"""
        return ["suite", "run"]


    def hydrate_suite(self, bundle):
        """suite is read-only on PUT
        suite.product must match run.productversion.product on CREATE
        """

        # CREATE
        if bundle.request.META['REQUEST_METHOD'] == 'POST':
            suite_id = self._id_from_uri(bundle.data['suite'])
            suite = Suite.objects.get(id=suite_id)
            run_id = self._id_from_uri(bundle.data['run'])
            run = Run.objects.get(id=run_id)
            if suite.product.id != run.productversion.product.id:
                error_message = str(
                    "suite's product must match run's product."
                )
                logger.error(
                    "\n".join([error_message, "suite prod: %s, run prod: %s"]),
                    suite.product.id, run.productversion.product.id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

        return bundle



class SuiteSelectionResource(BaseSelectionResource):
    """
    Specialty end-point for an AJAX call from the multi-select widget
    for selecting suites.
    """

    product = fields.ForeignKey(ProductResource, "product")
    runs = fields.ToManyField(RunResource, "runs")
    created_by = fields.ForeignKey(
        UserResource, "created_by", full=True, null=True)

    class Meta:
        queryset = Suite.objects.all().select_related(
            "created_by",
            ).annotate(case_count=Count("cases"))

        list_allowed_methods = ['get']
        fields = ["id", "name", "created_by"]
        filtering = {
            "product": ALL_WITH_RELATIONS,
            "runs": ALL_WITH_RELATIONS,
            "created_by": ALL_WITH_RELATIONS,
            }
        ordering = ["runs"]


    def dehydrate(self, bundle):
        """Add some convenience fields to the return JSON."""

        suite = bundle.obj
        bundle.data["suite_id"] = unicode(suite.id)
        bundle.data["case_count"] = suite.case_count
        bundle.data["filter_cases"] = filter_url("manage_cases", suite)

        return bundle

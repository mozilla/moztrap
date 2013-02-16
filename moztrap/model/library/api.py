from tastypie import http, fields
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from ..core.api import (ProductVersionResource, ProductResource,
                        UserResource)
from .models import CaseVersion, Case, Suite, CaseStep, SuiteCase
from ...model.core.models import ProductVersion
from ..mtapi import MTResource, MTAuthorization
from ..environments.api import EnvironmentResource
from ..tags.api import TagResource

import logging
logger = logging.getLogger(__name__)


class SuiteCaseAuthorization(MTAuthorization):
    """Atypically named permission."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "library.manage_suite_cases"



class CaseVersionAuthorization(MTAuthorization):
    """A permission of 'library.manage_caseversions does not exist,
    use library.manage_cases instead."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "library.manage_cases"



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



class CaseResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for Case.

    Filterable by suites and product fields.
    """

    suites = fields.ToManyField(SuiteResource, "suites", readonly=True)
    product = fields.ForeignKey(ProductResource, "product")

    class Meta(MTResource.Meta):
        queryset = Case.objects.all()
        fields = ["id", "suites", "product", "idprefix"]
        filtering = {
            "suites": ALL_WITH_RELATIONS,
            "product": ALL_WITH_RELATIONS,
            }

    @property
    def model(self):
        """Model class related to this resource."""
        return Case


    def hydrate_product(self, bundle):
        """product is read-only on PUT"""
        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            case = self.get_via_uri(bundle.request.path)
            prod_id = self._id_from_uri(bundle.data['product'])
            if str(case.product.id) != prod_id:
                error_msg = "product of an existing case may not be changed."
                logger.error(
                    "\n".join([error_msg, "old: %s, new: %s"]),
                    case.product.id, prod_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_msg))

        return bundle



class CaseStepResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for CaseSteps.

    Filterable by caseversion field.
    """

    caseversion = fields.ForeignKey(
        "moztrap.model.library.api.CaseVersionResource", "caseversion")

    class Meta(MTResource.Meta):
        queryset = CaseStep.objects.all()
        fields = ["id", "caseversion", "instruction", "expected", "number"]
        filtering = {
            "caseversion": ALL_WITH_RELATIONS,
        }
        ordering = ["number", "id"]
        authorization = CaseVersionAuthorization()

    @property
    def model(self):
        """Model class related to this resource."""
        return CaseStep


    def hydrate_caseversion(self, bundle):
        """caseversion is read-only on PUT
        """
        if 'caseversion' not in bundle.data.keys():
            return bundle

        # edit (PUT)
        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            cs = self.get_via_uri(bundle.request.path)
            cv_id = self._id_from_uri(bundle.data['caseversion'])
            if str(cs.caseversion.id) != cv_id:
                error_message = str(
                    "caseversion of an existing casestep " +
                    "may not be changed.")
                logger.error(
                    "\n".join([error_message, "old: %s, new: %s"]),
                    cs.caseversion.id, cv_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

        return bundle



class SuiteCaseResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for SuiteCase.

    Filterable by suite and case fields.
    """

    case = fields.ForeignKey(CaseResource, 'case')
    suite = fields.ForeignKey(SuiteResource, 'suite')

    class Meta(MTResource.Meta):
        queryset = SuiteCase.objects.all()
        fields = ["suite", "case", "order", "id"]
        filtering = {
            "suite": ALL_WITH_RELATIONS,
            "case": ALL_WITH_RELATIONS
        }
        authorization = SuiteCaseAuthorization()

    @property
    def model(self):
        return SuiteCase

    def hydrate_case(self, bundle):
        """case is read-only on PUT
        case.product must match suite.product on CREATE
        """

        # edit (PUT)
        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            if 'case' not in bundle.data.keys():
                return bundle
            sc = self.get_via_uri(bundle.request.path)
            case_id = self._id_from_uri(bundle.data['case'])
            if str(sc.case.id) != case_id:
                error_message = str(
                    "case of an existing suitecase " +
                    "may not be changed.")
                logger.error(
                    "\n".join([error_message, "old: %s, new: %s"]),
                    sc.case.id, case_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

            return bundle

        # CREATE
        case_id = self._id_from_uri(bundle.data['case'])
        case = Case.objects.get(id=case_id)
        suite_id = self._id_from_uri(bundle.data['suite'])
        suite = Suite.objects.get(id=suite_id)
        if case.product.id != suite.product.id:
            error_message = str(
                "case's product must match suite's product."
            )
            logger.error(
                "\n".join([error_message, "case prod: %s, suite prod: %s"]),
                case.product.id, suite.product.id)
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest(error_message))

        return bundle


    def hydrate_suite(self, bundle):
        """suite is read-only on PUT
        """

        # edit (PUT)
        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            if 'suite' not in bundle.data.keys():
                return bundle
            sc = self.get_via_uri(bundle.request.path)
            suite_id = self._id_from_uri(bundle.data['suite'])
            if str(sc.suite.id) != suite_id:
                error_message = str(
                    "suite of an existing suitecase " +
                    "may not be changed.")
                logger.error(
                    "\n".join([error_message, "old: %s, new: %s"]),
                    sc.suite.id, suite_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

        return bundle



class CaseVersionResource(MTResource):
    """
    Create, Read, Update and Delete capabilities for CaseVersions.

    Filterable by environments, productversion, case, and tags fields.
    """

    case = fields.ForeignKey(CaseResource, "case")
    steps = fields.ToManyField(
        CaseStepResource, "steps", full=True, readonly=True)
    environments = fields.ToManyField(
        EnvironmentResource, "environments", full=True, readonly=True)
    productversion = fields.ForeignKey(
        ProductVersionResource, "productversion")
    tags = fields.ToManyField(TagResource, "tags", full=True, readonly=True)
    #@@@ attachments


    class Meta(MTResource.Meta):
        queryset = CaseVersion.objects.all()
        fields = ["id", "name", "description", "case", "status"]
        filtering = {
            "environments": ALL,
            "productversion": ALL_WITH_RELATIONS,
            "case": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            }
        authorization = CaseVersionAuthorization()

    @property
    def model(self):
        """Model class related to this resource."""
        return CaseVersion


    def hydrate_productversion(self, bundle):
        """productversion is read-only on PUT
        case.product must match productversion.product on CREATE
        """
        if 'productversion' not in bundle.data.keys():
            return bundle

        # edit (PUT)
        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            cv = self.get_via_uri(bundle.request.path)
            pv_id = self._id_from_uri(bundle.data['productversion'])
            if str(cv.productversion.id) != pv_id:
                error_message = str(
                    "productversion of an existing caseversion " +
                    "may not be changed.")
                logger.error(
                    "\n".join([error_message, "old: %s, new: %s"]),
                    cv.productversion.id, pv_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

            return bundle

        # create
        pv_id = self._id_from_uri(bundle.data['productversion'])
        pv = ProductVersion.objects.get(id=pv_id)
        case_id = self._id_from_uri(bundle.data['case'])
        case = Case.objects.get(id=case_id)
        if not case.product.id == pv.product.id:
            message = str("productversion must match case's product")
            logger.error("\n".join([message,
                "productversion product id: %s case product id: %s"], ),
                pv.product.id,
                case.product.id)
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest(message))

        return bundle


    def hydrate_case(self, bundle):
        """case is a primary key and as such is not editable."""

        if bundle.request.META['REQUEST_METHOD'] == 'PUT':
            if 'case' not in bundle.data.keys():
                return bundle

            cv = self.get_via_uri(bundle.request.path)
            case_id = self._id_from_uri(bundle.data['case'])
            if str(cv.case.id) != case_id:
                error_message = str(
                    "case of an existing caseversion may not be changed.")
                logger.error(
                    "\n".join([error_message, "old: %s, new: %s"]),
                    cv.case.id, case_id)
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest(error_message))

        return bundle



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

        if hasattr(request, 'GET'):  # pragma: no cover
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
                key = key[:-4]  # Stripping out trailing ``__ne``
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
    productversion = fields.ForeignKey(
        ProductVersionResource, "productversion")
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
            suite_id = int(bundle.request.GET["case__suites"])
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

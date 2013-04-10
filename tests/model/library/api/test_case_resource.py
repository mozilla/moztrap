"""
Tests for CaseResource api.

"""

from tests.case.api.crud import ApiCrudCases
from tests import case

import logging
mozlogger = logging.getLogger('moztrap.test')



class CaseResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseFactory()


    @property
    def resource_name(self):
        return "case"


    @property
    def permission(self):
        """String defining the permission required for
        Create, Update, and Delete.
        """
        return "library.manage_cases"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        shortdatetime = self.datetime.split("-")[-1]
        self.product_fixture = self.F.ProductFactory.create()

        fields = {
            u'product': unicode(
                self.get_detail_url("product", str(self.product_fixture.id))),
            u'idprefix': unicode("%s" % shortdatetime),
            u'suites': [],
        }

        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Case.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        actual = {}
        actual[u"resource_uri"] = unicode(
            self.get_detail_url(self.resource_name, str(backend_obj.id)))
        actual[u"id"] = unicode(str(backend_obj.id))
        actual[u"product"] = unicode(
            self.get_detail_url("product", str(backend_obj.product.id)))
        actual[u"idprefix"] = unicode(backend_obj.idprefix)
        actual[u"suites"] = [unicode(
            self.get_detail_url("suite", str(suite.id))
                ) for suite in backend_obj.suites.all()]

        return actual


    @property
    def read_create_fields(self):
        """List of fields that are required for create but read-only for update."""
        return ["product"]

    # overrides from crud.py

    # additional test cases, if any

    # validation cases

    @property
    def _ro_message(self):
        return "product of an existing case may not be changed."



class CaseSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory


    @property
    def resource_name(self):
        return "caseselection"

    @property
    def included_param(self):
        return "case__suites"


    @property
    def available_param(self):
        return "{0}__ne".format(self.included_param)


    def get_exp_obj(self, cv):
        """Return an expected caseselection object with fields filled."""
        return {
            u"case": unicode(
                self.get_detail_url("case", cv.case.id)),
            u"case_id": unicode(cv.case.id),
            u"created_by": None,
            u"id": unicode(cv.id),
            u"latest": True,
            u"name": unicode(cv.name),
            u"product": {
                u"id": unicode(cv.productversion.product_id)
            },
            u"product_id": unicode(cv.productversion.product_id),
            u"productversion": unicode(
                self.get_detail_url("productversion", cv.productversion.id)),
            u"resource_uri": unicode(
                self.get_detail_url("caseselection", cv.id)),
            u"tags": [],
            }


    def get_exp_meta(self, count=0):
        """Return an expected meta object with count field filled"""
        return {
            "limit": 20,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": count,
            }


    def _do_test(self, for_id, filter_param, exp_objects):
        params = {filter_param: for_id}

        res = self.get_list(params=params)
        self.assertEqual(res.status_int, 200)

        act = res.json

        self.maxDiff = None
        self.assertEquals(self.get_exp_meta(len(exp_objects)), act["meta"])
        self.assertEqual(exp_objects, act["objects"])


    def test_available_for_none_included(self):
        """Get a list of available cases, none included"""

        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")

        self._do_test(
            -1,
            self.available_param,
            [self.get_exp_obj(cv) for cv in [cv1, cv2]],
            )


    def _setup_two_included(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        suite = self.F.SuiteFactory.create()
        sc1 = self.F.SuiteCaseFactory.create(
            case=cv1.case, suite=suite, order=0)
        sc2 = self.F.SuiteCaseFactory.create(
            case=cv2.case, suite=suite, order=1)

        return {
            "cv1": cv1,
            "cv2": cv2,
            "s": suite,
            "sc1": sc1,
            "sc2": sc2,
            }


    def test_available_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()
        self._do_test(
            data["s"].id,
            self.available_param,
            [],
            )


    def test_included_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()

        exp_objects = [
            self.get_exp_obj(
                cv,
                ) for cv, sc in [
                    (data["cv1"], data["sc1"]),
                    (data["cv2"], data["sc2"]),
                    ]
                ]

        self._do_test(
            data["s"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def _setup_for_one_included_one_not(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        suite = self.F.SuiteFactory.create()
        sc1 = self.F.SuiteCaseFactory.create(
            case=cv1.case,
            suite=suite,
            )
        return {
            "cv1": cv1,
            "cv2": cv2,
            "s": suite,
            "sc1": sc1,
            }


    def test_available_for_one_included_one_not(self):
        """Get a list of available cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv2"])]

        self._do_test(
            data["s"].id,
            self.available_param,
            exp_objects=exp_objects,
            )


    def test_included_for_one_included_one_not(self):
        """Get a list of included cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [
            self.get_exp_obj(
                cv,
                ) for cv, sc in [(data["cv1"], data["sc1"])]
            ]

        self._do_test(
            data["s"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def test_case_without_version(self):
        """Get a list of available cases, skip ones without versions"""

        # create a case with no version
        self.F.CaseFactory()

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv2"])]

        self._do_test(
            data["s"].id,
            self.available_param,
            exp_objects=exp_objects,
            )

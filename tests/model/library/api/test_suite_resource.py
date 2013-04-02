"""
Tests for SuiteResource api.

"""
import json

from tests import case
from tests.case.api.crud import ApiCrudCases



class SuiteResourceTest(ApiCrudCases):
    """Please see the test cases implemented in tests.case.api.ApiCrudCases.

    The following abstract methods must be implemented:
      - factory(self)                           (property)
      - resource_name(self)                     (property)
      - permission(self)                        (property)
      - new_object_data(self)                   (property)
      - backend_object(self, id)                (method)
      - backend_data(self, backend_object)      (method)
      - backend_meta_data(self, backend_object) (method)

    """

    # implementations for abstract methods and properties

    @property
    def factory(self):
        """The factory to use to create fixtures of the object under test.
        """
        return self.F.SuiteFactory()


    @property
    def resource_name(self):
        """String defining the resource name.
        """
        return "suite"


    @property
    def permission(self):
        """String defining the permission required for
        Create, Update, and Delete.
        """
        return "library.manage_suites"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        self.product_fixture = self.F.ProductFactory.create()
        modifiers = (self.datetime, self.resource_name)
        fields = {
            u"name": unicode("test_%s_%s" % modifiers),
            u"description": unicode("test %s %s" % modifiers),
            u"product": unicode(self.get_detail_url(
                "product", self.product_fixture.id)),
            u"status": unicode("draft"),
        }
        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Suite.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        actual = {}
        actual[u"id"] = unicode(str(backend_obj.id))
        actual[u"name"] = unicode(backend_obj.name)
        actual[u"description"] = unicode(backend_obj.description)
        actual[u"product"] = unicode(
                        self.get_detail_url("product", backend_obj.product.id))
        actual[u"status"] = unicode(backend_obj.status)
        actual[u"resource_uri"] = unicode(
            self.get_detail_url(self.resource_name, str(backend_obj.id)))

        return actual


    @property
    def read_create_fields(self):
        """List of fields that are required for create but read-only for update."""
        return ["product"]

    # additional test cases, if any



class SuiteSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.SuiteFactory


    @property
    def resource_name(self):
        return "suiteselection"


    @property
    def included_param(self):
        return "runs"


    @property
    def available_param(self):
        return "{0}__ne".format(self.included_param)


    def get_exp_obj(self, s, runs=[], order=None):
        """Return an expected suiteselection object with fields filled."""

        return {
            u"case_count": s.cases.count(),
            u"created_by": None,
            u"filter_cases":
                u"/manage/cases/?filter-suite={0}".format(s.id),
            u"id": unicode(s.id),
            u"name": unicode(s.name),
            u"runs": runs,
            u"order": order,
            u"product": unicode(
                self.get_detail_url("product", s.product.id)),
            u"resource_uri": unicode(
                self.get_detail_url("suiteselection", s.id)),
            u"suite_id": unicode(s.id)
        }


    def get_exp_meta(self, count=0):
        """Return an expected meta object with count field filled"""
        return {
            u"limit": 20,
            u"next": None,
            u"offset": 0,
            u"previous": None,
            u"total_count": count,
            }


    def _do_test(self, for_id, filter_param, exp_objects):
        params = {filter_param: for_id}

        res = self.get_list(params=params)
        self.assertEqual(res.status_int, 200)

        act = res.json

        self.maxDiff = None
        self.assertEquals(act["meta"], self.get_exp_meta(len(exp_objects)))
        self.assertEqual(exp_objects, act["objects"])


    def test_available_for_none_included(self):
        """Get a list of available suites, none selected"""

        s1 = self.factory.create(name="Suite1")
        s2 = self.factory.create(name="Suite2")

        self._do_test(
            -1,
            self.available_param,
            [self.get_exp_obj(s) for s in [s1, s2]],
            )


    def _setup_two_included(self):
        s1 = self.factory.create(name="Suite1")
        s2 = self.factory.create(name="Suite2")
        run = self.F.RunFactory.create()
        runsuite1 = self.F.RunSuiteFactory.create(
            run=run, suite=s1, order=0)
        runsuite2 = self.F.RunSuiteFactory.create(
            run=run, suite=s2, order=1)
        return {
            "run": run,
            "s1": s1,
            "s2": s2,
            "runsuite1": runsuite1,
            "runsuite2": runsuite2,
            }


    def test_available_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()
        self._do_test(
            data["run"].id,
            self.available_param,
            [],
            )


    def test_included_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()

        exp_objects = [self.get_exp_obj(
            s,
            [unicode(self.get_detail_url("run", data["run"].id))],
            rs.order,
            ) for s, rs in [
                (data["s1"], data["runsuite1"]),
                (data["s2"], data["runsuite2"])]]

        self._do_test(
            data["run"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def _setup_for_one_included_one_not(self):
        s1 = self.factory.create(name="Suite1")
        s2 = self.factory.create(name="Suite2")
        run = self.F.RunFactory.create()
        runsuite1 = self.F.RunSuiteFactory.create(
            run=run, suite=s1, order=0)
        return {
            "run": run,
            "s1": s1,
            "s2": s2,
            "runsuite1": runsuite1,
            }


    def test_available_for_one_included_one_not(self):
        """Get a list of available cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["s2"])]

        self._do_test(
            data["run"].id,
            self.available_param,
            exp_objects=exp_objects,
            )


    def test_included_for_one_included_one_not(self):
        """Get a list of included cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(
            data["s1"],
            [unicode(self.get_detail_url("run", data["run"].id))],
            data["runsuite1"].order,
            )]

        self._do_test(
            data["run"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def test_available_included_in_other_runs(self):
        """Get a list of available suites, when suites included elsewhere"""

        s1 = self.factory.create(name="Suite1")
        s2 = self.factory.create(name="Suite2")
        run1 = self.F.RunFactory.create()
        runsuite1 = self.F.RunSuiteFactory.create(
            run=run1, suite=s1, order=0)
        runsuite2 = self.F.RunSuiteFactory.create(
            run=run1, suite=s2, order=1)
        run2 = self.F.RunFactory.create()
        runsuite3 = self.F.RunSuiteFactory.create(
            run=run2, suite=s1, order=0)
        runsuite4 = self.F.RunSuiteFactory.create(
            run=run2, suite=s2, order=1)

        self._do_test(
            -1,
            self.available_param,
            [self.get_exp_obj(
                s,
                runs=[
                    unicode(self.get_detail_url("run", run1.id)),
                    unicode(self.get_detail_url("run", run2.id)),
                    ],
                order=rs.order
                ) for s, rs in [(s1, runsuite3), (s2, runsuite4)]],
            )

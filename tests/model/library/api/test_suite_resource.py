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


    # additional test cases, if any



class SuiteSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.SuiteFactory


    @property
    def resource_name(self):
        return "suiteselection"


    def test_none_selected_available(self):
        """Get a list of available suites, none selected"""

        s1 = self.factory.create(name="Suite1")
        s2 = self.factory.create(name="Suite2")

        res = self.get_list()
        self.assertEqual(res.status_int, 200)

        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 2,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = []
        for s in [s1, s2]:

            exp_objects.append(
                {
                    u"created_by": None,
                    u"id": unicode(s.id),
                    u"name": unicode(s.name),
                    u"runs": [],
                    u"order": None,
                    u"product": unicode(
                        self.get_detail_url("product",s.product.id)),
                    u"resource_uri": unicode(
                        self.get_detail_url("suiteselection",s.id)),
                    u"suite_id": unicode(s.id)
                })


        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def _setup_two_selected(self):
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

    def test_available_for_all_selected(self):
        """Get a list of available cases, both selected"""

        run = self._setup_two_selected()["run"]
        res = self.get_list(params={"runs__ne": run.id})
        self.assertEqual(res.status_int, 200)

        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 0,
            }

        self.assertEquals(act_meta, exp_meta)
        self.assertEquals(act["objects"], [])


    def test_two_selected(self):
        """Get a list of available cases, both selected"""

        data = self._setup_two_selected()
        res = self.get_list(params={"runs": data["run"].id})
        self.assertEqual(res.status_int, 200)

        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 2,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = []
        for s, runsuite in [
            (data["s1"], data["runsuite1"]),
            (data["s2"], data["runsuite2"])]:

            exp_objects.append(
                {
                    u"created_by": None,
                    u"id": unicode(s.id),
                    u"name": unicode(s.name),
                    u"order": runsuite.order,
                    u'runs': [self.get_detail_url("run", data["run"].id)],
                    u"product": unicode(
                        self.get_detail_url("product",s.product.id)),
                    u"resource_uri": unicode(
                        self.get_detail_url("suiteselection",s.id)),
                    u"suite_id": unicode(s.id)
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def _setup_one_selected_one_not(self):
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


    def test_available_for_one_selected_one_not(self):
        """Get a list of cases for a suite, one selected, one not."""

        data = self._setup_one_selected_one_not()
        res = self.get_list(params={"runs__ne": data["run"].id})
        self.assertEqual(res.status_int, 200)
        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 1,
            }

        self.assertEquals(exp_meta, act_meta)

        def get_suite(s, order):
            return [{
                        u"created_by": None,
                        u"id": unicode(s.id),
                        u"name": unicode(s.name),
                        u"order": order,
                        u"runs": [],
                        u"product": unicode(
                            self.get_detail_url("product",s.product.id)),
                        u"resource_uri": unicode(
                            self.get_detail_url("suiteselection",s.id)),
                        u"suite_id": unicode(s.id)
                    }]

        self.maxDiff = None
        self. assertEqual(
            get_suite(data["s2"], None),
            act["objects"],
            )


    def test_selected_for_one_selected_one_not(self):
        """Get a list of cases for a suite, one selected, one not."""

        data = self._setup_one_selected_one_not()
        res = self.get_list(params={"runs": data["run"].id})
        self.assertEqual(res.status_int, 200)
        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 1,
            }

        self.assertEquals(act_meta, exp_meta)

        def get_suite(s, order):
            return [{
                        u"created_by": None,
                        u"id": unicode(s.id),
                        u"name": unicode(s.name),
                        u"order": order,
                        u'runs': [self.get_detail_url("run", data["run"].id)],
                        u"product": unicode(
                            self.get_detail_url("product",s.product.id)),
                        u"resource_uri": unicode(
                            self.get_detail_url("suiteselection",s.id)),
                        u"suite_id": unicode(s.id)
                    }]

        self.maxDiff = None
        self. assertEqual(
            get_suite(data["s1"], data["runsuite1"].order),
            act["objects"],
            )

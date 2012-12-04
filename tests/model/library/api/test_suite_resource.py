"""
Tests for SuiteResource api.

"""
import json

from tests import case



class SuiteResourceTest(case.api.ApiTestCase):

    @property
    def resource_name(self):
        return "suite"

    def test_create_delete_suite(self):
        # user = self.F.UserFactory.create(permissions=["library.manage_suites"])
        user = self.F.UserFactory.create(is_superuser=True)
        apikey = self.F.ApiKeyFactory.create(owner=user)
        params = {"username": user.username, "api_key": apikey.key}

        product_fixture = self.F.ProductFactory.create()
        fields = {
            'name': 'test_create_delete_suite',
            'description': 'test_create_delete_suite',
            'product': unicode(self.get_detail_url("product",product_fixture.id)),
            'status': 'active',
        }

        res = self.post(
            self.get_list_url(self.resource_name),
            params=params,
            payload=fields,
            )

        res = self.get_list()

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

        act_objects = act["objects"]
        exp_objects = [{}] #XXX finish this expected result!

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


class SuiteCaseSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory


    @property
    def resource_name(self):
        return "suitecaseselection"


    def test_none_selected(self):
        """Get a list of available cases, none selected"""

        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")

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
        self.assertEquals(act["objects"]["selected"], [])

        act_objects = act["objects"]["unselected"]
        exp_objects = []
        for cv in [cv1, cv2]:

            exp_objects.append(
                {
                    u'case': unicode(
                        self.get_detail_url("case",cv.case.id)),
                    u'case_id': unicode(cv.case.id),
                    u'created_by': None,
                    u'id': unicode(cv.id),
                    u'name': unicode(cv.name),
                    u'order': None,
                    u'product': {
                        u'id': unicode(cv.productversion.product_id)
                    },
                    u'product_id': unicode(cv.productversion.product_id),
                    u'productversion': unicode(
                        self.get_detail_url("productversion",cv.productversion.id)),
                    u'resource_uri': unicode(
                        self.get_detail_url("suitecaseselection",cv.id)),
                    u'tags': [],
                })


        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def test_two_selected(self):
        """Get a list of available cases, both selected"""

        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        suite = self.F.SuiteFactory.create()
        suitecase1 = self.F.SuiteCaseFactory.create(
            case=cv1.case, suite=suite, order=0)
        suitecase2 = self.F.SuiteCaseFactory.create(
            case=cv2.case, suite=suite, order=1)

        res = self.get_list(params={"for_suite": suite.id})
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
        self.assertEquals(act["objects"]["unselected"], [])

        act_objects = act["objects"]["selected"]
        exp_objects = []
        for cv, suitecase in [(cv1, suitecase1), (cv2, suitecase2)]:

            exp_objects.append(
                {
                    u'case': unicode(
                        self.get_detail_url("case",cv.case.id)),
                    u'case_id': unicode(cv.case.id),
                    u'created_by': None,
                    u'id': unicode(cv.id),
                    u'name': unicode(cv.name),
                    u'order': suitecase.order,
                    u'product': {
                        u'id': unicode(cv.productversion.product_id)
                    },
                    u'product_id': unicode(cv.productversion.product_id),
                    u'productversion': unicode(
                        self.get_detail_url("productversion",
                            cv.productversion.id)),
                    u'resource_uri': unicode(
                        self.get_detail_url("suitecaseselection",cv.id)),
                    u'tags': [],
                    })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def test_one_selected_one_not(self):
        """Get a list of cases for a suite, one selected, one not."""

        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        suite = self.F.SuiteFactory.create()
        suitecase1 = self.F.SuiteCaseFactory.create(
            case=cv1.case,
            suite=suite,
            order=0,
            )

        res = self.get_list(params={"for_suite": suite.id})
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

        def get_case(cv, order):
            return [{
                u'case': unicode(
                    self.get_detail_url("case",cv.case.id)),
                u'case_id': unicode(cv.case.id),
                u'created_by': None,
                u'id': unicode(cv.id),
                u'name': unicode(cv.name),
                u'order': order,
                u'product': {
                    u'id': unicode(cv.productversion.product_id)
                },
                u'product_id': unicode(cv.productversion.product_id),
                u'productversion': unicode(
                    self.get_detail_url("productversion",cv.productversion.id)),
                u'resource_uri': unicode(
                    self.get_detail_url("suitecaseselection",cv.id)),
                u'tags': [],
                }]

        self.maxDiff = None
        self. assertEqual(
            get_case(cv1, suitecase1.order),
            act["objects"]["selected"],
            )
        self. assertEqual(
            get_case(cv2, None),
            act["objects"]["unselected"],
            )

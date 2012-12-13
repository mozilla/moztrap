"""
Tests for SuiteResource api.

"""
import json

from tests import case
from tests.case.api.crud import ApiCrudCases



class SuiteResourceTest(ApiCrudCases):
    """Please see the test cases in tests.case.api.ApiCrudCases.
    The following abstract methods must be implemented:
    * resource_name (property)
    * permission (property)
    * new_object_data (property)
    * backend_object (property)
    * backend_data(backend_object)
    * backend_meta_data(backend_object)
    """

    # implementations for abstract methods and properties

    @property
    def resource_name(self):
        return "suite"

    @property
    def permission(self):
        return "library.manage_suites"

    @property
    def new_object_data(self):
        '''produces data dictionary for use in create'''
        self.product_fixture = self.F.ProductFactory.create()
        modifiers = (self.datetime, self.resource_name)
        fields = {
            u'name': unicode('test_%s_%s' % modifiers),
            u'description': unicode('test %s %s' % modifiers),
            u'product': unicode(self.get_detail_url("product",self.product_fixture.id)),
            u'status': unicode('draft'),
        }
        return fields

    def backend_object(self, id):
        """get the object from the backend"""
        return self.model.Suite.everything.get(id=id)
 
    def backend_data(self, backend_obj):
        """dictionary containing the data expected from get detail for an object,
        using data pulled from the db. both keys and data should be in unicode"""
        actual = {}
        actual[u'id'] = unicode(str(backend_obj.id))
        actual[u'name'] = unicode(backend_obj.name)
        actual[u'description'] = unicode(backend_obj.description)
        actual[u'product'] = unicode(
                        self.get_detail_url("product", backend_obj.product.id))
        actual[u'status'] = unicode(backend_obj.status)
        actual[u'resource_uri'] = unicode(self.get_detail_url(self.resource_name, 
                                                              str(backend_obj.id)))

        return actual

    def backend_meta_data(self, backend_obj):
        '''retrieves object meta data from backend'''
        actual = {}
        try:
            actual['created_by'] = backend_obj.created_by.username
        except AttributeError:
            actual['created_by'] = None
        try:
            actual['modified_by'] = backend_obj.modified_by.username
        except AttributeError:
            actual['modified_by'] = None
        try:
            actual['deleted_by'] = backend_obj.deleted_by.username
        except AttributeError:
            actual['deleted_by'] = None

        actual['created_on'] = backend_obj.created_on
        actual['modified_on'] = backend_obj.modified_on
        actual['deleted_on'] = backend_obj.deleted_on

        return actual

    # additional test cases, if any
        

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

"""
Tests for CaseResource api.

"""

from tests import case



class CaseResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseFactory


    @property
    def resource_name(self):
        return "case"


    def test_case_list(self):
        """Get a list of existing cases"""

        case1 = self.factory.create()
        case2 = self.factory.create()

        res = self.get_list()

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
        for case in [case1, case2]:

            exp_objects.append({
                u"id": unicode(case.id),
                u"suites": [],
                u"resource_uri": unicode(self.get_detail_url("case",case.id)),
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)



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


    def get_exp_obj(self, cv, order=None):
        """Return an expected caseselection object with fields filled."""
        return {
            u'case': unicode(
                self.get_detail_url("case",cv.case.id)),
            u'case_id': unicode(cv.case.id),
            u'created_by': None,
            u'id': unicode(cv.id),
            u'latest': True,
            u'name': unicode(cv.name),
            u'order': order,
            u'product': {
                u'id': unicode(cv.productversion.product_id)
            },
            u'product_id': unicode(cv.productversion.product_id),
            u'productversion': unicode(
                self.get_detail_url("productversion",cv.productversion.id)),
            u'resource_uri': unicode(
                self.get_detail_url("caseselection",cv.id)),
            u'tags': [],
            }


    def get_exp_meta(self, count=0):
        """Return an expected meta object with count field filled"""
        return {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : count,
            }


    def _do_test(self, for_id, filter_param, exp_objects):
        params={filter_param: for_id}

        res = self.get_list(params=params)
        self.assertEqual(res.status_int, 200)

        act = res.json

        self.maxDiff = None
        self.assertEquals(act["meta"], self.get_exp_meta(len(exp_objects)))
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

        exp_objects = [self.get_exp_obj(cv, order=sc.order) for cv, sc in [
            (data["cv1"], data["sc1"]),
            (data["cv2"], data["sc2"]),
            ]]

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
            order=0,
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
        exp_objects = [self.get_exp_obj(cv, order=sc.order) for cv, sc in [
            (data["cv1"], data["sc1"]),
            ]]

        self._do_test(
            data["s"].id,
            self.included_param,
            exp_objects=exp_objects,
            )

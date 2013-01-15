"""
Tests for CaseVersionResource api.

"""

from tests import case



class CaseVersionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory


    @property
    def resource_name(self):
        return "caseversion"


    def test_caseversion_list(self):
        """Get a list of existing caseversions"""

        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        casestep1 = self.F.CaseStepFactory.create(caseversion=cv1)
        casestep2 = self.F.CaseStepFactory.create(caseversion=cv2)
        suitecase1 = self.F.SuiteCaseFactory.create(case=cv1.case)
        suitecase2 = self.F.SuiteCaseFactory.create(case=cv2.case)

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
        for cv, suitecase, casestep in [(cv1, suitecase1, casestep1), 
                                        (cv2, suitecase2, casestep2)]:

            exp_objects.append({
                u"case": {
                    u"id": unicode(cv.case.id),
                    u"suites": [{u"name": u"Test Suite",
                                 u"id": unicode(suitecase.suite.id),
                                 u"status": u"active",
                                 u"description": u"",
                                 u"product": unicode(
                                    self.get_detail_url(
                                        "product", suitecase.suite.product.id)),
                                 u"resource_uri": unicode(
                                    self.get_detail_url(
                                        "suite", suitecase.suite.id))
                                 }],
                    u"resource_uri": unicode(
                        self.get_detail_url("case",cv.case.id)),
                    },
                u"description": unicode(cv.description),
                u"environments": [],
                u"id": unicode(cv.id),
                u"name": unicode(cv.name),
                u"productversion": unicode(
                    self.get_detail_url("productversion",cv.productversion.id)),
                u"resource_uri": unicode(
                    self.get_detail_url("caseversion",cv.id)),
                u"steps": [{u"expected": u"",
                            u"instruction": u"Test step instruction",
                            u"resource_uri": unicode(
                                self.get_detail_url("casestep",casestep.id))
                            }],
                u"tags": [],
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)



class CaseVersionSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory


    @property
    def resource_name(self):
        return "caseversionselection"

    @property
    def included_param(self):
        return "tags"


    @property
    def available_param(self):
        return "{0}__ne".format(self.included_param)


    def get_exp_obj(self, cv, tags=[]):
        """Return an expected caseselection object with fields filled."""

        exp_tags = []
        for t in tags:
            exp_tag = {
                u'id': unicode(t.id),
                u'name': unicode(t.name),
                u'description': unicode(t.description),
                u'resource_uri': unicode(self.get_detail_url("tag",t.id)),
                u'product': None,
                }
            if t.product:
                exp_tag[u'product'] = unicode(
                    self.get_detail_url("product", str(t.product.id)))
            exp_tags.append(exp_tag)

        return {
            u'case': unicode(
                self.get_detail_url("case",cv.case.id)),
            u'case_id': unicode(cv.case.id),
            u'created_by': None,
            u'id': unicode(cv.id),
            u'latest': True,
            u'name': unicode(cv.name),
            u'product': {
                u'id': unicode(cv.productversion.product_id)
            },
            u'product_id': unicode(cv.productversion.product_id),
            u'productversion': {
                u'codename': u'',
                u'id': unicode(cv.productversion.id),
                u'product': unicode(self.get_detail_url(
                    "product",
                    cv.productversion.product_id)),
                u'resource_uri': unicode(self.get_detail_url(
                    "productversion",
                    cv.productversion.id)),
                u'version': u'1.0'},
            u'productversion_name': unicode(cv.productversion.name),
            u'resource_uri': unicode(
                self.get_detail_url("caseversionselection",cv.id)),
            u'tags': exp_tags,
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

        cv1 = self.factory.create(name="Case1")
        cv2 = self.factory.create(name="Case2")

        self._do_test(
            -1,
            self.available_param,
            [self.get_exp_obj(cv) for cv in [cv1, cv2]],
            )


    def _setup_two_included(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        tag = self.F.TagFactory.create()
        cv1.tags.add(tag)
        cv2.tags.add(tag)

        return {
            "cv1": cv1,
            "cv2": cv2,
            "t": tag,
            }


    def test_available_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()
        self._do_test(
            data["t"].id,
            self.available_param,
            [],
            )


    def test_included_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()

        exp_objects = [self.get_exp_obj(cv, tags=[data["t"]]) for cv in [
            data["cv1"], data["cv2"]]]

        self._do_test(
            data["t"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def _setup_for_one_included_one_not(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        tag = self.F.TagFactory.create()
        cv1.tags.add(tag)

        return {
            "cv1": cv1,
            "cv2": cv2,
            "t": tag,
            }


    def test_available_for_one_included_one_not(self):
        """Get a list of available cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv2"])]

        self._do_test(
            data["t"].id,
            self.available_param,
            exp_objects=exp_objects,
            )


    def test_included_for_one_included_one_not(self):
        """Get a list of included cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv1"], tags=[data["t"]])]

        self._do_test(
            data["t"].id,
            self.included_param,
            exp_objects=exp_objects,
            )

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
        for cv in [cv1, cv2]:

            exp_objects.append({
                u"case": {
                    u"id": unicode(cv.case.id),
                    u"resource_uri": unicode(self.get_detail_url("case",cv.case.id)),
                    },
                u"description": unicode(cv.description),
                u'environments': [],
                u"id": unicode(cv.id),
                u"name": unicode(cv.name),
                u"productversion": unicode(self.get_detail_url("productversion",cv.productversion.id)),
                u"resource_uri": unicode(self.get_detail_url("caseversion",cv.id)),
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)

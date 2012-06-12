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
                u"resource_uri": unicode(self.get_detail_uri("case",case.id)),
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)

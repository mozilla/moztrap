"""
Tests for ResultResource api.

"""

from tests import case



class ResultResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.RunCaseVersionFactory


    @property
    def resource_name(self):
        return "result"


    def test_submit_results(self):
        """Get a list of existing test runs"""
        r1 = self.F.RunFactory.create(name="RunA")

        c1 = self.F.CaseVersionFactory.create(name="Case1", description="ab")
        c2 = self.F.CaseVersionFactory.create(name="Case2", description="cd")

        rcv1 = self.factory.create(caseversion=c1, run=r1)
        rcv2 = self.factory.create(caseversion=c2, run=r1)

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
        for rcv in [rcv1, rcv2]:
            cv = rcv.caseversion

            exp_objects.append({
                u"caseversion": {
                    u"case": unicode(self.get_detail_uri("case",cv.case.id)),
                    u"description": unicode(cv.description),
                    u'environments': [],
                    u"id": unicode(cv.id),
                    u"name": unicode(cv.name),
                    u"resource_uri": unicode(self.get_detail_uri("caseversion",cv.id)),
                    },
                u"id": unicode(rcv.id),
                u"run_id": unicode(rcv.run.id),
                u"run": unicode(self.get_detail_uri("run",rcv.run.id)),
                u"resource_uri": unicode(self.get_detail_uri("runcaseversion",rcv.id)),
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def test_runcaseversion_by_id(self):
        """Get a single test run, by id"""
        r = self.F.RunFactory.create(name="RunA")
        cv = self.F.CaseVersionFactory.create(name="Case1")
        rcv = self.factory.create(caseversion=cv, run=r)

        res = self.get_detail(rcv.id)
        self.assertEqual(res.status_int, 200, res)

        act = res.json
        self.assertEqual(
            unicode(self.get_detail_uri("runcaseversion", rcv.id)),
            act["resource_uri"],
            )

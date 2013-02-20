"""
Tests for RunCaseVersionResource api.

"""

from tests import case



class RunCaseVersionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.RunCaseVersionFactory


    @property
    def resource_name(self):
        return "runcaseversion"


    def test_runcaseversion_list(self):
        """Get a list of existing runcaseversions"""
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
            "limit": 20,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": 2,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = []
        for rcv in [rcv1, rcv2]:
            cv = rcv.caseversion

            exp_objects.append({
                u"caseversion": {
                    u"case": unicode(self.get_detail_url("case", cv.case.id)),
                    u"description": unicode(cv.description),
                    u'environments': [],
                    u"id": unicode(cv.id),
                    u"name": unicode(cv.name),
                    u"productversion": unicode(self.get_detail_url(
                        "productversion",
                        cv.productversion.id)),
                    u"resource_uri": unicode(self.get_detail_url(
                        "caseversion",
                        cv.id,
                        )),
                    u'steps': [],
                    u'tags': [],
                    u'status': unicode(cv.status),
                    },
                u"id": unicode(rcv.id),
                u"run": unicode(self.get_detail_url("run", rcv.run.id)),
                u"resource_uri": unicode(self.get_detail_url(
                    "runcaseversion",
                    rcv.id,
                    )),
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)

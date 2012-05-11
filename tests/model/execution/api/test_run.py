"""
Tests for RunResource api.

"""

from tests import case


class RunResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.RunFactory


    @property
    def resource_name(self):
        return "run"


    def test_run_list(self):
        """Get a list of existing test runs"""
        r1 = self.factory.create(name="Foo", description="this")
        pv = r1.productversion
        r2 = self.factory.create(
            name="Bar",
            description="that",
            productversion=pv,
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
            "total_count" : 2,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = []
        for exp_run in [r1, r2]:
            exp_objects.append({
                u"description": unicode(exp_run.description),
                u'environments': [],
                u"id": unicode(exp_run.id),
                u"name": unicode(exp_run.name),
                u"product_name": unicode(pv.product.name),
                u"productversion": u"/api/v1/productversion/{0}/".format(pv.id),
                u"productversion_name": unicode(pv.version),
                u"resource_uri": u"/api/v1/run/{0}/".format(exp_run.id),
                u"status": u"draft",
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def test_run_list_filtered_status(self):
        r1 = self.factory.create(name="Foo", description="this")
        r2 = self.factory.create(name="Bar", description="that", status="active")

        res = self.get_list(params={"status": "active"})
        self.assertEqual(res.status_int, 200)

        act = res.json["objects"]
        self.assertEqual(len(act), 1, "expect 1 item in list")
        self.assertEqual(unicode(r2.name), act[0]["name"])


    def test_run_list_filtered_productversion(self):
        r1 = self.factory.create(name="Foo", description="this")
        pv = self.F.ProductVersionFactory.create(version="3.14")
        r2 = self.factory.create(
            name="Bar",
            description="that",
            productversion=pv,
            )

        res = self.get_list(params={"productversion__version": "3.14"})
        self.assertEqual(res.status_int, 200)

        act = res.json["objects"]
        self.assertEqual(len(act), 1, "expect 1 item in list")
        self.assertEqual(unicode(r2.name), act[0]["name"])


    def test_run_by_id(self):
        """Get a single test run, by id"""
        r = self.factory(name="Floo")

        res = self.get_detail(r.id)
        self.assertEqual(res.status_int, 200, res)

        act = res.json
        self.assertEqual(unicode(r.name), act["name"])


    def test_run_by_id_environments(self):
        """Get a single test run, by id"""
        r = self.factory(name="Floo")

        res = self.get_detail(r.id)
        self.assertEqual(res.status_int, 200, res)

        act = res.json
        self.assertEqual(unicode(r.name), act["name"])




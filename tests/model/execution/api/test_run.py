"""
Tests for RunResource api.

"""

from tests import case


class RunResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for Runs."""
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
        assert Fail, "needs environments, uri only"

        res = self.get_list()

        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 2,
            }

        self.assertEquals(act["meta"], exp_meta)

        act_objects = res.json["objects"]
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


    def test_run_authentication(self):
        assert False, "needs impl"


    def test_run_authorization(self):
        assert False, "needs impl"


    def test_post_run_results(self):
        """
        Validate the run is created correctly, plus all the results.
        """
        assert False, "needs impl"


    def test_run_by_id_shows_env_detail(self):
        """Get a single test run, by id shows expanded deatil for environments"""
        r = self.factory(name="Floo")

        res = self.get_detail(r.id)

        self.assertEqual(unicode(r.name), res.json["name"])
        assert False, "needs impl"






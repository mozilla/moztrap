"""
Tests for RunResource api.

"""

from tests import case
from moztrap.model.execution.models import Run
import json


class RunResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for Runs."""
        return self.F.RunFactory


    @property
    def resource_name(self):
        return "run"


    def x_test_run_list(self):
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


    def xtest_run_by_id_shows_env_detail(self):
        """Get a single test run, by id shows expanded deatil for environments"""
        r = self.factory(name="Floo")

        res = self.get_detail(r.id)

        self.assertEqual(unicode(r.name), res.json["name"])
        assert False, "needs impl"


    def xtest_run_no_authentication(self):
        assert False, "needs impl"


    def xtest_run_no_authorization(self):
        assert False, "needs impl"


    def xtest_post_run_results(self):
        """
        Validate the run is created correctly, plus all the results.
        """
        assert False, "needs impl"


    def test_submit_new_run_with_results(self):
        """Submit a new test run with results."""

        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
        )
        c_i = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
        )
        c_f = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
        )

        pv_res = self.get(self.get_list_url("product"))
        print pv_res.json

        c_res = self.get(self.get_list_url("case"))
        print c_res.json

        cv_res = self.get(self.get_list_url("caseversion"))
        print cv_res.json

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": {
                "description": "a description",
                "environments": [
                    self.get_detail_uri("environment", envs[0].id),
                ],
                "name": "atari autorun.sys",
                "productversion": self.get_detail_uri("productversion", pv.id),
                "runcaseversions": [
                    {"case": unicode(c_i.case.id),
                    "comment": "what the hellfire?",
                    "environment": unicode(envs[0].id),
                    "status": "invalidated",
                    },
                    {"case": unicode(c_p.case.id),
                     "environment": unicode(envs[0].id),
                     "status": "passed"
                    },
                    {"bug": "http://www.deathvalleydogs.com",
                    "case": unicode(c_f.case.id),
                    "comment": "dang thing...",
                    "environment": unicode(envs[0].id),
                    "status": "failed",
                    "stepnumber": 0
                    },
                ],
                "status": "active"
            }
        }

        """
        Going through with the debugger, it looks like the productversion
        is "not found".  But compared the URI with use_connect and it looks right.
        I wonder if the creation with the factory isn't working right?
        """
        res = self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=params,
            )

        self.assertEqual("atari autorun.sys", Run.objects.get().name)





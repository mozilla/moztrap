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


    @property
    def auth_params(self):
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        return {"username": user.username, "api_key": apikey.key}


    def test_run_list(self):
        """Get a list of existing test runs"""
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        r1 = self.factory.create(
            name="Foo",
            description="this",
            environments=envs,
            )
        pv = r1.productversion
        r2 = self.factory.create(
            name="Bar",
            description="that",
            productversion=pv,
            environments=envs,
            )

        res = self.get_list(params=self.auth_params)

        exp_meta = {
            "limit": 20,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": 2,
            }

        self.assertEquals(res.json["meta"], exp_meta)

        act_objects = res.json["objects"]
        # make the envs a set, for comparison.
        for ao in act_objects:
            ao["environments"] = set(ao["environments"])

        exp_objects = []
        for exp_run in [r1, r2]:
            exp_objects.append({
                u"description": unicode(exp_run.description),
                u'environments': set([
                    unicode(self.get_detail_url("environment", envs[0].id)),
                    unicode(self.get_detail_url("environment", envs[1].id)),
                    ]),
                u"id": unicode(exp_run.id),
                u"name": unicode(exp_run.name),
                u"product_name": unicode(pv.product.name),
                u"productversion": u"/api/v1/productversion/{0}/".format(pv.id),
                u"productversion_name": unicode(pv.version),
                u"resource_uri": u"/api/v1/run/{0}/".format(exp_run.id),
                u"runcaseversions": [],
                u"status": u"draft",
                })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)


    def test_run_by_id_shows_env_detail(self):
        """Get a single test run, by id shows expanded detail for environments"""
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"]})
        r = self.factory(name="Floo", environments=envs)

        res = self.get_detail(r.id, params=self.auth_params)

        exp_objects = {
            u'elements': [
                {u'category':
                     {u'resource_uri': unicode(self.get_detail_url(
                         "category",
                         envs[0].elements.get().category.id),
                        ),
                      u'id': unicode(envs[0].elements.get().category.id),
                      u'name': u'OS'
                     },
                 u'resource_uri': unicode(self.get_detail_url(
                     "element",
                     envs[0].elements.get().id),
                 ),
                 u'id': unicode(envs[0].elements.get().id),
                 u'name': u'OS X'
                }],
            u'id': unicode(envs[0].id),
            u'resource_uri': unicode(self.get_detail_url(
                "environment",
                envs[0].id),
                )
            }

        self.assertEqual(unicode(r.name), res.json["name"], res.json)
        self.assertEqual(res.json["environments"][0], exp_objects)


    def test_submit_new_run_with_results(self):
        """Submit a new test run with results."""

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
        self.F.CaseStepFactory(caseversion=c_f)

        # submit results for these cases
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
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
                     "stepnumber": 1
                },
            ],
            "status": "active"
        }

        res = self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=self.auth_params,
            )

        # verify run
        run = self.model.Run.objects.get()
        self.assertEqual("atari autorun.sys", run.name)

        # verify returned content
        self.assertEqual(
            res.json["ui_uri"],
            u"/results/cases/?filter-run={0}".format(run.id),
            )

        # verify runcaseversions
        for cv in [c_f, c_p, c_i]:
            rcv = self.model.RunCaseVersion.objects.get(caseversion__id=cv.id)
            self.assertEqual(rcv.run.id, run.id)

        # verify pass results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_p)
        self.assertEqual(result.status, "passed")
        self.assertEqual(result.environment, envs[0])

        # verify fail results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_f)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.comment, "dang thing...")

        self.assertEqual(set(result.bug_urls()), set(["http://www.deathvalleydogs.com"]))
        self.assertEqual(result.environment, envs[0])

        # verify invalid results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_i)
        self.assertEqual(result.status, "invalidated")
        self.assertEqual(result.environment, envs[0])
        self.assertEqual(result.comment, "what the hellfire?")


    def test_submit_new_run_bad_case_id(self):
        """Submit a new test run for a case that doesn't exist."""

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)

        # submit results for these cases
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                    {"case": unicode(2),
                     "environment": unicode(envs[0].id),
                     "status": "passed"
                },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=self.auth_params,
            status=400,
            )


    def test_submit_new_run_bad_env_id(self):
        """Submit a new test run with results."""

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                {"case": unicode(c_p.case.id),
                     "environment": unicode(envs[0].id + 1),
                     "status": "passed"
                     },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=self.auth_params,
            status=400,
            )


    def test_submit_new_run_with_missing_status_field(self):
        """
        Submit a new test run with bad results data.

        No status in the runcaseversion.
        """

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                {"case": unicode(c_p.case.id),
                 "environment": unicode(envs[0].id),
                },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=self.auth_params,
            status=400,
            )


    def test_run_no_authentication(self):
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                    {"case": unicode(c_p.case.id),
                     "environment": unicode(envs[0].id),
                     "status": "passed"
                },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            status=401,
            )


    def test_run_bad_api_key(self):
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        params = {"username": user.username, "api_key": "abc123"}
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                    {"case": unicode(c_p.case.id),
                     "environment": unicode(envs[0].id),
                     "status": "passed"
                },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=params,
            status=401,
            )


    def test_submit_run_no_authorization(self):
        user = self.F.UserFactory.create(
            username="foo",
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                {"case": unicode(c_p.case.id),
                 "environment": unicode(envs[0].id),
                 "status": "passed"
                 },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=params,
            status=401,
            )


    def test_submit_run_no_user(self):

        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            )

        # submit results for these cases
        params = {"username": "foo", "api_key": "abc123"}
        payload = {
            "description": "a description",
            "environments": [
                self.get_detail_url("environment", envs[0].id),
                ],
            "name": "atari autorun.sys",
            "productversion": self.get_detail_url("productversion", pv.id),
            "runcaseversions": [
                    {"case": unicode(c_p.case.id),
                     "environment": unicode(envs[0].id),
                     "status": "passed"
                },
            ],
            "status": "active"
        }

        self.post(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=params,
            status=401,
            )

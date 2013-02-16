"""
Tests for ResultResource api.

This is a write-only resource via ``patch``.  So no read for lists, etc.
This works by providing results for an existing test run.

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


    def test_submit_results_for_run(self):
        """Submit results for an existing test run."""
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )
        c_i = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="InvalidCase",
            )
        c_f = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="FailCase",
            )
        self.F.CaseStepFactory(caseversion=c_f)

        self.factory.create(caseversion=c_p, run=r1, environments=envs)
        self.factory.create(caseversion=c_i, run=r1, environments=envs)
        self.factory.create(caseversion=c_f, run=r1, environments=envs)

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "passed"
                },
                    {
                    "case": c_i.case.id,
                    "comment": "why u no make sense??",
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "invalidated"
                },
                    {
                    "bug": "http://www.deathvalleydogs.com",
                    "case": c_f.case.id,
                    "comment": "why u no pass?",
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "failed",
                    "stepnumber": 1
                }
            ]
        }


        res = self.patch(
            self.get_list_url(self.resource_name),
            params=params,
            payload=payload,
            )

#        assert False, res.text

        # verify pass results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_p)
        self.assertEqual(result.status, "passed")
        self.assertEqual(result.environment, envs[0])

        # verify fail results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_f)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.comment, "why u no pass?")
        self.assertEqual(set(result.bug_urls()), set(["http://www.deathvalleydogs.com"]))
        self.assertEqual(result.environment, envs[0])

        # verify invalid results
        result = self.model.Result.objects.get(runcaseversion__caseversion=c_i)
        self.assertEqual(result.status, "invalidated")
        self.assertEqual(result.environment, envs[0])
        self.assertEqual(result.comment, "why u no make sense??")


    def test_submit_results_for_run_no_status(self):
        """Submit results for an existing test run without a status."""
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )

        self.factory.create(caseversion=c_p, run=r1)

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                }
            ]
        }

        res = self.patch(
            self.get_list_url(self.resource_name),
            params=params,
            payload=payload,
            status=400,
            )


    def test_submit_results_for_run_bad_env_id(self):
        """Submit results for an existing test run with a bad env id."""
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )

        self.factory.create(caseversion=c_p, run=r1)

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id + 1,
                    "run_id": r1.id,
                    "status": "passed",
                    }
            ]
        }

        res = self.patch(
            self.get_list_url(self.resource_name),
            params=params,
            payload=payload,
            status=400,
            )


    def test_submit_results_for_run_no_runcaseversion(self):
        """Submit results for an existing test run when a runcaseversion doesn't exist."""
        user = self.F.UserFactory.create(
            username="foo",
            permissions=["execution.execute"],
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "passed"
                },
            ]
        }

        res = self.patch(
            self.get_list_url(self.resource_name),
            params=params,
            payload=payload,
            status=400,
            )


    def test_submit_results_for_run_no_authentication(self):
        """Submit results for an existing test run by non-user."""
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )

        self.factory.create(caseversion=c_p, run=r1)

        # submit results for these cases
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "passed"
                }
            ]
        }

        res = self.patch(
            self.get_list_url(self.resource_name),
            payload=payload,
            status=401,
            )


    def test_submit_results_for_run_no_authorization(self):
        """Submit results for an existing test run by user without perms."""
        user = self.F.UserFactory.create(
            username="foo",
            )
        apikey = self.F.ApiKeyFactory.create(owner=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        r1 = self.F.RunFactory.create(name="RunA", productversion=pv)

        c_p = self.F.CaseVersionFactory.create(
            case__product=pv.product,
            productversion=pv,
            name="PassCase",
            )

        self.factory.create(caseversion=c_p, run=r1)

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.case.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "passed"
                }
            ]
        }

        res = self.patch(
            self.get_list_url(self.resource_name),
            payload=payload,
            params=params,
            status=401,
            )

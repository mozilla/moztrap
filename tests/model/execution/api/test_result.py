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
        apikey = self.F.ApiKeyFactory.create(user=user)
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X", "Linux"]})
        r1 = self.F.RunFactory.create(name="RunA", environments=envs)

        c_p = self.F.CaseVersionFactory.create(
            productversion = r1.productversion,
            name="PassCase",
            )
        c_i = self.F.CaseVersionFactory.create(
            productversion = r1.productversion,
            name="InvalidCase",
            )
        c_f = self.F.CaseVersionFactory.create(
            productversion = r1.productversion,
            name="FailCase",
            )

        rcv_p = self.factory.create(caseversion=c_p, run=r1)
        rcv_i = self.factory.create(caseversion=c_i, run=r1)
        rcv_f = self.factory.create(caseversion=c_f, run=r1)

        # submit results for these cases
        params = {"username": user.username, "api_key": apikey.key}
        payload = {
            "objects": [
                    {
                    "case": c_p.id,
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "passed"
                },
                    {
                    "case": c_i.id,
                    "comment": "why u no make sense??",
                    "environment": envs[0].id,
                    "run_id": r1.id,
                    "status": "invalidated"
                },
                    {
                    "bug": "http://www.deathvalleydogs.com",
                    "case": c_f.id,
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
        assert False, "need to figure out how to patch data"



    def test_submit_results_for_run_no_perm(self):
        """Submit results for an existing test run by user without perms."""
        assert False, "needs impl, exp failure"

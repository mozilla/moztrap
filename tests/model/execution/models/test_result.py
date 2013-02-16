"""
Tests for Result model.

"""
from tests import case



class ResultTest(case.DBTestCase):
    """Tests for Result."""
    def test_unicode(self):
        env = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        r = self.F.ResultFactory(
            status="started",
            runcaseversion__run__name="FF10",
            runcaseversion__caseversion__name="Open URL",
            tester__username="tester",
            environment=env,
            )

        self.assertEqual(
            unicode(r),
            u"Case 'Open URL' included in run 'FF10', "
            "run by tester in English, OS X: started")


    def test_bug_urls(self):
        """Result.bug_urls aggregates bug urls from step results, sans dupes."""
        r = self.F.ResultFactory()
        self.F.StepResultFactory.create(result=r)
        self.F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug1")
        self.F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug1")
        self.F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            r.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )


    def test_save_old_result_doesnt_become_latest(self):
        """Saving an older result doesn't mark it as latest."""
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"], "Language": ["English"]})
        run = self.F.RunFactory.create(environments=envs)
        rcv = self.F.RunCaseVersionFactory.create(run=run)
        u = self.F.UserFactory.create()

        rcv.result_pass(envs[0], user=u)
        r1 = rcv.results.get(is_latest=True)

        rcv.result_fail(envs[0], user=u)
        r2 = rcv.results.get(is_latest=True)

        r1 = self.refresh(r1)
        r1.comment = "this is it"
        r1.save()

        r1 = self.refresh(r1)
        r2 = self.refresh(r2)

        self.assertEqual(r2.status, "failed")
        self.assertEqual(r2.is_latest, True)
        self.assertEqual(r1.is_latest, False)

"""Tests for template tags/filters for running tests."""
import datetime

from django.template import Template, Context

import mock

from tests import case



class ResultForTest(case.DBTestCase):
    """Tests for the result_for template tag."""
    def result_for(self, runcaseversion, user, environment, render):
        """Execute template tag with given args and render given string."""
        t = Template(
            "{% load execution %}{% result_for rcv user env as result %}"
            + render)
        return t.render(
            Context({"rcv": runcaseversion, "user": user, "env": environment}))


    def test_result_exists(self):
        """If the result already exists, it is returned."""
        r = self.F.ResultFactory()

        self.assertEqual(
            self.result_for(
                r.runcaseversion, r.tester, r.environment, "{{ result.id }}"),
            str(r.id)
            )


    def test_dupe_results_keeps_completed(self):
        """If dupe results exists, keep the one that's completed."""
        r = self.F.ResultFactory(status="passed")
        self.F.ResultFactory(
            tester=r.tester,
            runcaseversion=r.runcaseversion,
            environment=r.environment,
            )

        self.assertEqual(
            self.result_for(
                r.runcaseversion, r.tester, r.environment, "{{ result.id }}"),
            str(r.id),
            )
        self.assertEqual(self.model.Result.objects.count(), 1)


    def test_dupe_complete_results_keeps_latest(self):
        """If dupe completed results exists, keep the last-modified."""

        with mock.patch("cc.model.ccmodel.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime.datetime(2012, 3, 24)
            r = self.F.ResultFactory(
                status="passed",
                )
            mock_utcnow.return_value = datetime.datetime(2012, 3, 25)
            r2 = self.F.ResultFactory(
                tester=r.tester,
                runcaseversion=r.runcaseversion,
                environment=r.environment,
                status="failed",
                )

        self.assertEqual(
            self.result_for(
                r.runcaseversion, r.tester, r.environment, "{{ result.id }}"),
            str(r2.id),
            )
        self.assertEqual(self.model.Result.objects.count(), 1)


    def test_dupe_incomplete_results_keeps_latest(self):
        """If dupe incomplete results exists, keep the last-modified."""

        with mock.patch("cc.model.ccmodel.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime.datetime(2012, 3, 24)
            r = self.F.ResultFactory()
            mock_utcnow.return_value = datetime.datetime(2012, 3, 25)
            r2 = self.F.ResultFactory(
                tester=r.tester,
                runcaseversion=r.runcaseversion,
                environment=r.environment,
                )

        self.assertEqual(
            self.result_for(
                r.runcaseversion, r.tester, r.environment, "{{ result.id }}"),
            str(r2.id),
            )
        self.assertEqual(self.model.Result.objects.count(), 1)


    def test_result_does_not_exist(self):
        """If the result does not exist, a new unsaved one is returned."""
        rcv = self.F.RunCaseVersionFactory.create()
        env = self.F.EnvironmentFactory.create()
        user = self.F.UserFactory.create()

        self.assertEqual(
            self.result_for(
                rcv,
                user,
                env,
                "{{ result.id }} {{ result.runcaseversion.id }} "
                "{{ result.environment.id }} {{ result.tester.id }}"),
            "None {0} {1} {2}".format(rcv.id, env.id, user.id)
            )



class StepResultForTest(case.DBTestCase):
    """Tests for the step_result_for template tag."""
    def result_for(self, result, step, render):
        """Execute template tag with given args and render given string."""
        t = Template(
            "{% load execution %}{% stepresult_for result step as stepresult %}"
            + render)
        return t.render(
            Context({"result": result, "step": step}))


    def test_stepresult_exists(self):
        """If the step result already exists, it is returned."""
        sr = self.F.StepResultFactory()

        self.assertEqual(
            self.result_for(
                sr.result, sr.step, "{{ stepresult.id }}"),
            str(sr.id)
            )


    def test_step_result_does_not_exist(self):
        """If the step result does not exist, a new unsaved one is returned."""
        r = self.F.ResultFactory.create()
        step = self.F.CaseStepFactory.create()

        self.assertEqual(
            self.result_for(
                r,
                step,
                "{{ stepresult.id }} {{ stepresult.result.id }} "
                "{{ stepresult.step.id }}"),
            "None {0} {1}".format(r.id, step.id)
            )


    def test_result_does_not_exist(self):
        """If given result is not saved, unsaved step result is returned."""
        r = self.F.ResultFactory.build()
        step = self.F.CaseStepFactory.create()

        self.assertEqual(
            self.result_for(
                r,
                step,
                "{{ stepresult.id }} {{ stepresult.result.id }} "
                "{{ stepresult.step.id }}"),
            "None None {0}".format(step.id)
            )

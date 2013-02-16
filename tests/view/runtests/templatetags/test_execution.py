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


    def test_dupe_complete_results_keeps_both_finds_latest(self):
        """If dupe completed results exists, find the last-modified."""

        with mock.patch("moztrap.model.mtmodel.utcnow") as mock_utcnow:
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
        self.assertEqual(self.model.Result.objects.count(), 2)


    def test_dupe_incomplete_results_keeps_both_finds_latest(self):
        """If dupe incomplete results exists, find the last-modified."""

        with mock.patch("moztrap.model.mtmodel.utcnow") as mock_utcnow:
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
        self.assertEqual(self.model.Result.objects.count(), 2)


    def test_dupe_latest_results_sets_non_latest_to_false(self):
        """If dupe latest results exists, keep the last-modified."""

        with mock.patch("moztrap.model.mtmodel.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime.datetime(2012, 3, 24)
            res1 = self.F.ResultFactory(
                status="passed",
            )
            mock_utcnow.return_value = datetime.datetime(2012, 3, 25)
            res2 = self.F.ResultFactory(
                tester=res1.tester,
                runcaseversion=res1.runcaseversion,
                environment=res1.environment,
                status="passed",
                )

            # manually set a non-latest result to is_latest=True
            # since res1 has already been saved, and has a pk assigned,
            # it will not try to set all the other results to NOT latest.
            mock_utcnow.return_value = datetime.datetime(2012, 3, 24)
            self.model.Result.objects.filter(pk=res1.pk).update(
                is_latest=True,
                )

        self.assertEqual(self.result_for(
                res1.runcaseversion,
                res1.tester,
                res1.environment,
                "{{ result.id }}",
                ), str(res2.id))
        self.assertEqual(self.model.Result.objects.count(), 2)
        self.assertEqual(
            self.model.Result.objects.get(is_latest=True).pk, res2.pk)


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


class SuitesForTest(case.DBTestCase):
    """Tests for the suites_for template tag."""

    def suites_for(self, run, runcaseversion, render):
        """Execute template tag with given args and render given string."""
        t = Template(
            "{% load execution %}{% suites_for run runcaseversion as suites %}"
            + render)
        return t.render(
            Context({"run": run, "runcaseversion": runcaseversion}))


    def test_multiple_source_suites(self):
        """Sets source suites for a caseversion in multiple included suites."""
        envs = self.F.EnvironmentFactory.create_set(["os"], ["Atari"])
        pv = self.F.ProductVersionFactory(environments=envs)
        tc = self.F.CaseFactory.create(product=pv.product)
        cv = self.F.CaseVersionFactory.create(
            case=tc, productversion=pv, status="active")

        ts1 = self.F.SuiteFactory.create(product=pv.product, status="active")
        self.F.SuiteCaseFactory.create(suite=ts1, case=tc)

        ts2 = self.F.SuiteFactory.create(product=pv.product, status="active")
        self.F.SuiteCaseFactory.create(suite=ts2, case=tc)

        r = self.F.RunFactory.create(productversion=pv, environments=envs)
        self.F.RunSuiteFactory.create(suite=ts1, run=r)
        self.F.RunSuiteFactory.create(suite=ts2, run=r)

        r.activate()

        self.assertEqual(
            self.suites_for(
                r,
                self.model.RunCaseVersion.objects.get(),
                "{% for suite in suites %}{{ suite.id }} {% endfor %}"),
            "{0} {1} ".format(ts1.id, ts2.id)
        )


    def test_source_suite(self):
        """Sets source suites for each runcaseversion."""
        envs = self.F.EnvironmentFactory.create_set(["os"], ["Atari"])
        pv = self.F.ProductVersionFactory(environments=envs)
        tc = self.F.CaseFactory.create(product=pv.product)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=pv, status="active")

        ts = self.F.SuiteFactory.create(product=pv.product, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=pv, environments=envs)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        rcv = r.runcaseversions.get()
        self.assertEqual(
            self.suites_for(
                r,
                self.model.RunCaseVersion.objects.get(),
                "{% for suite in suites %}{{ suite.id }} {% endfor %}"),
            "{0} ".format(ts.id)
        )

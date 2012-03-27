"""
Tests for StepResult model.

"""
from tests import case



class StepResultTest(case.DBTestCase):
    def test_unicode(self):
        env = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        step = self.F.CaseStepFactory.create(
            caseversion__name="Open URL")

        sr = self.F.StepResultFactory.create(
            status=self.model.StepResult.STATUS.passed,
            step=step,
            result__status=self.model.Result.STATUS.started,
            result__runcaseversion__run__name="FF10",
            result__runcaseversion__caseversion=step.caseversion,
            result__tester__username="tester",
            result__environment=env,
            )

        self.assertEqual(
            unicode(sr),
            u"Case 'Open URL' included in run 'FF10', "
            "run by tester in English, OS X: started (step #%s: passed)"
            % step.number)

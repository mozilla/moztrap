"""
Tests for Run model.

"""
import datetime

from django.core.exceptions import ValidationError

from tests import case



class RunTest(case.DBTestCase):
    def test_unicode(self):
        r = self.F.RunFactory(name="Firefox 10 final run")

        self.assertEqual(unicode(r), u"Firefox 10 final run")


    def test_invalid_dates(self):
        """Run validates that start date is not after end date."""
        today = datetime.date(2011, 12, 13)
        r = self.F.RunFactory(
            start=today,
            end=today-datetime.timedelta(days=1))

        with self.assertRaises(ValidationError):
            r.full_clean()


    def test_valid_dates(self):
        """Run validation allows start date before or same as end date."""
        today = datetime.date(2011, 12, 13)
        r = self.F.RunFactory(
            start=today,
            end=today+datetime.timedelta(days=1))

        r.full_clean()


    def test_parent(self):
        """A Run's ``parent`` property returns its ProductVersion."""
        r = self.F.RunFactory()

        self.assertIs(r.parent, r.productversion)


    def test_own_team(self):
        """If ``has_team`` is True, Run's team is its own."""
        r = self.F.RunFactory.create(has_team=True)
        u = self.F.UserFactory.create()
        r.own_team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, Run's team is its parent's."""
        r = self.F.RunFactory.create(has_team=False)
        u = self.F.UserFactory.create()
        r.productversion.team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_clone(self):
        """Cloning a run returns a new, distinct Run with "Cloned: " name."""
        r = self.F.RunFactory.create(name="A Run")

        new = r.clone()

        self.assertNotEqual(new, r)
        self.assertIsInstance(new, type(r))
        self.assertEqual(new.name, "Cloned: A Run")


    def test_clone_sets_draft(self):
        """Clone of active run is still draft."""
        r = self.F.RunFactory.create(status="active")

        new = r.clone()

        self.assertEqual(new.status, "draft")


    def test_default_draft(self):
        """New run defaults to draft state."""
        r = self.F.RunFactory.create()

        self.assertEqual(r.status, "draft")


    def test_clone_included_suite(self):
        """Cloning a run clones member RunSuites."""
        rs = self.F.RunSuiteFactory.create()

        new = rs.run.clone()

        self.assertNotEqual(new.runsuites.get(), rs)


    def test_clone_no_run_caseversions(self):
        """Cloning a run does not clone member RunCaseVersions."""
        rcv = self.F.RunCaseVersionFactory.create()

        new = rcv.run.clone()

        self.assertEqual(new.runcaseversions.count(), 0)


    def test_clone_environments(self):
        """Cloning a Run clones its environments."""
        r = self.F.RunFactory(environments={"OS": ["OS X", "Linux"]})

        new = r.clone()

        self.assertEqual(len(new.environments.all()), 2)


    def test_clone_environments_narrowed(self):
        """Cloning a Run clones its environments exactly, even if narrowed."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory(environments=envs)
        r = self.F.RunFactory(productversion=pv, environments=envs[1:])

        self.assertEqual(len(r.environments.all()), 1)

        new = r.clone()

        self.assertEqual(len(new.environments.all()), 1)


    def test_clone_team(self):
        """Cloning a Run clones its team."""
        r = self.F.RunFactory(team=["One", "Two"])

        new = r.clone()

        self.assertEqual(len(new.team.all()), 2)


    def test_gets_productversion_envs(self):
        """A new test run inherits the environments of its product version."""
        pv = self.F.ProductVersionFactory.create(
            environments={"OS": ["Windows", "Linux"]})

        r = self.F.RunFactory.create(productversion=pv)

        self.assertEqual(set(r.environments.all()), set(pv.environments.all()))


    def test_inherits_env_removal(self):
        """Removing an env from a productversion cascades to run."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        run = self.F.RunFactory.create(productversion=pv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs[1:]))


    def test_draft_run_inherits_env_addition(self):
        """Adding an env to a productversion cascades to a draft run."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs[1:])
        run = self.F.RunFactory.create(productversion=pv, status="draft")

        pv.add_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs))


    def test_active_run_does_not_inherit_env_addition(self):
        """Adding env to a productversion does not cascade to an active run."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs[1:])
        run = self.F.RunFactory.create(productversion=pv, status="active")

        pv.add_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs[1:]))


    def test_result_summary(self):
        """``result_summary`` returns dict summarizing result states."""
        r = self.F.RunFactory()
        rcv1 = self.F.RunCaseVersionFactory(run=r)
        rcv2 = self.F.RunCaseVersionFactory(run=r)

        self.F.ResultFactory(runcaseversion=rcv1, status="assigned")
        self.F.ResultFactory(runcaseversion=rcv2, status="started")
        self.F.ResultFactory(runcaseversion=rcv1, status="passed")
        self.F.ResultFactory(runcaseversion=rcv2, status="failed")
        self.F.ResultFactory(runcaseversion=rcv1, status="failed")
        self.F.ResultFactory(runcaseversion=rcv2, status="invalidated")
        self.F.ResultFactory(runcaseversion=rcv1, status="invalidated")
        self.F.ResultFactory(runcaseversion=rcv2, status="invalidated")

        self.assertEqual(
            r.result_summary(),
            {
                "passed": 1,
                "failed": 2,
                "invalidated": 3
                }
            )


    def test_result_summary_specific(self):
        """``result_summary`` doesn't return results from other runs."""
        r = self.F.RunFactory()
        rcv = self.F.RunCaseVersionFactory(run=r)
        self.F.ResultFactory(runcaseversion=rcv, status="passed")

        r2 = self.F.RunFactory()

        self.assertEqual(
            r2.result_summary(),
            {
                "passed": 0,
                "failed": 0,
                "invalidated": 0
                }
            )


    def test_completion_percentage(self):
        """``completion`` returns fraction of case/env combos completed."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows", "Linux"]})
        pv = self.F.ProductVersionFactory(environments=envs)
        run = self.F.RunFactory(productversion=pv)
        rcv1 = self.F.RunCaseVersionFactory(
            run=run, caseversion__productversion=pv)
        rcv2 = self.F.RunCaseVersionFactory(
            run=run, caseversion__productversion=pv)

        self.F.ResultFactory(
            runcaseversion=rcv1, environment=envs[0], status="passed")
        self.F.ResultFactory(
            runcaseversion=rcv1, environment=envs[0], status="failed")
        self.F.ResultFactory(
            runcaseversion=rcv2, environment=envs[1], status="started")

        self.assertEqual(run.completion(), 0.25)


    def test_completion_percentage_empty(self):
        """If no runcaseversions, ``completion`` returns zero."""
        run = self.F.RunFactory()

        self.assertEqual(run.completion(), 0)



class RunActivationTest(case.DBTestCase):
    """Tests for activating runs and locking-in runcaseversions."""
    def setUp(self):
        """Set up envs, product and product versions used by all tests."""
        self.envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"], "Browser": ["Firefox", "Chrome"]})
        self.p = self.F.ProductFactory.create()
        self.pv8 = self.F.ProductVersionFactory.create(
            product=self.p, version="8.0", environments=self.envs)
        self.pv9 = self.F.ProductVersionFactory.create(
            product=self.p, version="9.0", environments=self.envs)



    def assertCaseVersions(self, run, caseversions):
        """Assert that ``run`` has (only) ``caseversions`` in it (any order)."""
        self.assertEqual(
            set([rcv.caseversion.id for rcv in run.runcaseversions.all()]),
            set([cv.id for cv in caseversions])
            )


    def assertOrderedCaseVersions(self, run, caseversions):
        """Assert that ``run`` has (only) ``caseversions`` in it (in order)."""
        self.assertEqual(
            [rcv.caseversion.id for rcv in run.runcaseversions.all()],
            [cv.id for cv in caseversions]
            )


    def test_productversion(self):
        """Selects test case version for run's product version."""
        tc = self.F.CaseFactory.create(product=self.p)
        tcv1 = self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv9, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [tcv1])


    def test_draft_not_included(self):
        """Only active test cases are considered."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="draft")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_only_active_suite(self):
        """Only test cases in an active suite are considered."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="draft")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        ts1 = self.F.SuiteFactory.create(product=self.p, status="locked")
        self.F.SuiteCaseFactory.create(suite=ts1, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_wrong_product_version_not_included(self):
        """Only caseversions for correct productversion are considered."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv9, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_no_environments_in_common(self):
        """Caseversion with no env overlap with run will not be included."""
        self.pv8.environments.add(*self.envs)

        tc = self.F.CaseFactory.create(product=self.p)
        tcv1 = self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")
        tcv1.remove_envs(*self.envs[:2])

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        r.remove_envs(*self.envs[2:])
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_ordering(self):
        """Suite/case ordering reflected in runcaseversion order."""
        tc1 = self.F.CaseFactory.create(product=self.p)
        tcv1 = self.F.CaseVersionFactory.create(
            case=tc1, productversion=self.pv8, status="active")
        tc2 = self.F.CaseFactory.create(product=self.p)
        tcv2 = self.F.CaseVersionFactory.create(
            case=tc2, productversion=self.pv8, status="active")
        tc3 = self.F.CaseFactory.create(product=self.p)
        tcv3 = self.F.CaseVersionFactory.create(
            case=tc3, productversion=self.pv8, status="active")

        ts1 = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts1, case=tc3, order=1)
        ts2 = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts2, case=tc2, order=1)
        self.F.SuiteCaseFactory.create(suite=ts2, case=tc1, order=2)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts2, run=r, order=1)
        self.F.RunSuiteFactory.create(suite=ts1, run=r, order=2)

        r.activate()

        self.assertOrderedCaseVersions(r, [tcv2, tcv1, tcv3])


    def test_sets_status_active(self):
        """Sets status of run to active."""
        r = self.F.RunFactory.create(status="draft")

        r.activate()

        self.assertEqual(self.refresh(r).status, "active")


    def test_already_active(self):
        """Has no effect on already-active run."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8, status="active")
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_disabled(self):
        """Sets disabled run to active but does not create runcaseversions."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8, status="disabled")
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])
        self.assertEqual(self.refresh(r).status, "active")


    def test_source_suite(self):
        """Sets source suites for each runcaseversion."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        rcv = r.runcaseversions.get()
        self.assertEqual(list(rcv.suites.all()), [ts])


    def test_multiple_source_suites(self):
        """Sets source suites for a caseversion in multiple included suites."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts1 = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts1, case=tc)

        ts2 = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts2, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts1, run=r)
        self.F.RunSuiteFactory.create(suite=ts2, run=r)

        r.activate()

        rcv = r.runcaseversions.get()
        self.assertEqual(set(rcv.suites.all()), set([ts1, ts2]))


    def test_removes_duplicate_runcaseversions(self):
        """
        Re-activating a run that has dupe runcaseversions cleans them up.

        Environments are set to current values; all results are preserved.

        """
        r = self.F.RunFactory.create(productversion=self.pv8, status="draft")
        rcv1 = self.F.RunCaseVersionFactory.create(
            run=r,
            caseversion__productversion=self.pv8,
            caseversion__status="active",
            )
        rcv1.environments.remove(self.envs[1])
        self.F.ResultFactory.create(runcaseversion=rcv1)
        rcv2 = self.F.RunCaseVersionFactory.create(
            caseversion=rcv1.caseversion, run=r)
        self.F.ResultFactory.create(runcaseversion=rcv2)
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=rcv1.caseversion.case)
        self.F.RunSuiteFactory.create(suite=ts, run=r)
        r.environments.remove(self.envs[0])

        r.activate()

        rcv = r.runcaseversions.get()
        self.assertEqual(set(rcv.environments.all()), set(self.envs[1:]))
        self.assertEqual(rcv.results.count(), 2)


    def test_updates_envs_on_previously_included_rcv(self):
        """Re-activating updates envs on previously-included caseversions."""
        r = self.F.RunFactory.create(productversion=self.pv8, status="draft")
        rcv = self.F.RunCaseVersionFactory.create(
            run=r,
            caseversion__productversion=self.pv8,
            caseversion__status="active",
            )
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=rcv.caseversion.case)
        self.F.RunSuiteFactory.create(suite=ts, run=r)
        rcv.caseversion.environments.remove(self.envs[0])

        r.activate()

        self.assertEqual(set(rcv.environments.all()), set(self.envs[1:]))


    def test_removes_draft_caseversions_and_their_results(self):
        """Re-activating removes caseversions that are now draft."""
        r = self.F.RunFactory.create(productversion=self.pv8, status="draft")
        rcv = self.F.RunCaseVersionFactory.create(
            run=r,
            caseversion__productversion=self.pv8,
            caseversion__status="draft",
            )
        self.F.ResultFactory.create(runcaseversion=rcv)
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=rcv.caseversion.case)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertEqual(r.runcaseversions.count(), 0)
        self.assertEqual(
            self.model.Result.objects.filter(runcaseversion__run=r).count(), 0)


    def test_removes_no_env_overlap_caseversions(self):
        """Re-activating removes caseversions that now have no env overlap."""
        r = self.F.RunFactory.create(productversion=self.pv8, status="draft")
        rcv = self.F.RunCaseVersionFactory.create(
            run=r,
            caseversion__productversion=self.pv8,
            caseversion__status="draft",
            )
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=rcv.caseversion.case)
        self.F.RunSuiteFactory.create(suite=ts, run=r)
        rcv.caseversion.environments.remove(self.envs[0])
        r.environments.remove(*self.envs[1:])

        r.activate()

        self.assertEqual(r.runcaseversions.count(), 0)

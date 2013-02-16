"""
Tests for Run model.

"""
import datetime
from mock import patch

from django.core.exceptions import ValidationError

from moztrap.model.execution.models import Run

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
            end=today - datetime.timedelta(days=1))

        with self.assertRaises(ValidationError):
            r.full_clean()


    def test_valid_dates(self):
        """Run validation allows start date before or same as end date."""
        today = datetime.date(2011, 12, 13)
        r = self.F.RunFactory(
            start=today,
            end=today + datetime.timedelta(days=1))

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


    def test_clone_for_series(self):
        """Clone of active run series makes a new run that is ready to run."""
        r = self.F.RunFactory.create(status="active", is_series=True)

        new = r.clone_for_series(build="ABERCIE")

        self.assertEqual(new.status, "draft")
        self.assertEqual(new.name, "Test Run - Build: ABERCIE")
        self.assertEqual(new.is_series, False)
        self.assertEqual(new.series, r)
        self.assertEqual(new.build, "ABERCIE")


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


    def test_soft_deleted_not_included(self):
        """Only active test cases are considered."""
        tc = self.F.CaseFactory.create(product=self.p)
        cv = self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(productversion=self.pv8)
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        cv.delete()
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


    def test_run_series_no_runcaseversions(self):
        """Run series don't get runcaseversions."""
        tc = self.F.CaseFactory.create(product=self.p)
        self.F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = self.F.RunFactory.create(
            productversion=self.pv8,
            status="draft",
            is_series=True)
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


    def test_removes_duplicate_runcaseversions(self):
        """
        Re-activating a run that has had a caseversion removed cleans them up.

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
        self.F.ResultFactory.create(runcaseversion=rcv1)
        rcv2 = self.F.RunCaseVersionFactory.create(
            run=r,
            caseversion__productversion=self.pv8,
            caseversion__status="active",
            )
        self.F.ResultFactory.create(runcaseversion=rcv2)
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.SuiteCaseFactory.create(suite=ts, case=rcv1.caseversion.case)
        # rcv2 is NOT in the suite, so should be removed during activate
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
        self.assertEqual(
            self.model.Result.objects.count(), 0)


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


    def test_query_count_on_activate(self):
        """
        Count number of queries needed for activation of complex run.

        Queries explained:
        ------------------

        Query 1: Get the environment ids from this run

            "SELECT `environments_environment`.`id` FROM
            `environments_environment` INNER JOIN
            `execution_run_environments` ON (`environments_environment`.`id`
             = `execution_run_environments`.`environment_id`) WHERE (
             `environments_environment`.`deleted_on` IS NULL AND
             `execution_run_environments`.`run_id` = 1 )",

        Query 2: Get the caseversion ids that SHOULD be included in this run,
            in order

            "SELECT DISTINCT cv.id as id
            FROM execution_run as r
                INNER JOIN execution_runsuite as rs
                    ON rs.run_id = r.id
                INNER JOIN library_suitecase as sc
                    ON rs.suite_id = sc.suite_id
                INNER JOIN library_suite as s
                    ON sc.suite_id = s.id
                INNER JOIN library_caseversion as cv
                    ON cv.case_id = sc.case_id
                    AND cv.productversion_id = r.productversion_id
                INNER JOIN library_caseversion_environments as cve
                    ON cv.id = cve.caseversion_id
            WHERE cv.status = 'active'
                AND s.status = 'active'
                AND rs.run_id = 1
                AND cve.environment_id IN (1,2,3,4)
            ORDER BY rs.order, sc.order
            ",

        Query 3-7: Get all the runcaseversions that are not in the result of
         Query 2
            to be used for delete. and then delete them.

            "SELECT `execution_runcaseversion`.`id`,
            `execution_runcaseversion`.`created_on`,
            `execution_runcaseversion`.`created_by_id`,
            `execution_runcaseversion`.`modified_on`,
            `execution_runcaseversion`.`modified_by_id`,
            `execution_runcaseversion`.`deleted_on`,
            `execution_runcaseversion`.`deleted_by_id`,
            `execution_runcaseversion`.`cc_version`,
            `execution_runcaseversion`.`run_id`, `execution_runcaseversion`
            .`caseversion_id`, `execution_runcaseversion`.`order` FROM
            `execution_runcaseversion` WHERE (`execution_runcaseversion`
            .`deleted_on` IS NULL AND `execution_runcaseversion`.`run_id` =
            1  AND NOT (`execution_runcaseversion`.`caseversion_id` IN (2,
            3, 4, 5, 6, 7))) ORDER BY `execution_runcaseversion`.`order` ASC",

            "SELECT `execution_result`.`id`, `execution_result`
            .`created_on`, `execution_result`.`created_by_id`,
            `execution_result`.`modified_on`,
            `execution_result`.`modified_by_id`,
            `execution_result`.`deleted_on`, `execution_result`
            .`deleted_by_id`, `execution_result`.`cc_version`,
            `execution_result`.`tester_id`, `execution_result`
            .`runcaseversion_id`, `execution_result`.`environment_id`,
            `execution_result`.`status`, `execution_result`.`comment`,
            `execution_result`.`is_latest`, `execution_result`.`review`,
            `execution_result`.`reviewed_by_id` FROM `execution_result`
            WHERE `execution_result`.`runcaseversion_id` IN (1)",

            "DELETE FROM `execution_runcaseversion_suites` WHERE
            `runcaseversion_id` IN (1)",

            "DELETE FROM `execution_runcaseversion_environments` WHERE
            `runcaseversion_id` IN (1)",

            "DELETE FROM `execution_runcaseversion` WHERE `id` IN (1)",

        Query 8: Get existing runcaseversions with the caseversion ids so we
         can use
            Them to build the new RunCaseVersion objects we will only be
            updated
            with order in the bulk create.

            "SELECT `execution_runcaseversion`.`id`,
            `execution_runcaseversion`.`caseversion_id` FROM
            `execution_runcaseversion` WHERE (`execution_runcaseversion`
            .`deleted_on` IS NULL AND `execution_runcaseversion`.`run_id` =
            1 ) ORDER BY `execution_runcaseversion`.`order` ASC",

        Query 9: bulk insert for RunCaseVersions, updates if already existing

            "INSERT INTO execution_runcaseversion (`id`, `created_on`,
            `created_by_id`, `modified_on`, `modified_by_id`, `deleted_on`,
            `deleted_by_id`, `cc_version`, `run_id`, `caseversion_id`,
            `order`) VALUES (NULL, '2012-11-20 00:11:25.417158', NULL,
            '2012-11-20 00:11:25.417176', NULL, NULL, NULL, 0, 1, 2, 1),
            (NULL, '2012-11-20 00:11:25.417239', NULL,
            '2012-11-20 00:11:25.417251', NULL, NULL, NULL, 0, 1, 3, 2),
            (NULL, '2012-11-20 00:11:25.417298', NULL,
            '2012-11-20 00:11:25.417310', NULL, NULL, NULL, 0, 1, 4, 3), (2,
             '2012-11-20 00:11:25.417353', NULL, '2012-11-20 00:11:25
             .417365', NULL, NULL, NULL, 0, 1, 5, 4), (NULL,
             '2012-11-20 00:11:25.417411', NULL, '2012-11-20 00:11:25
             .417423', NULL, NULL, NULL, 0, 1, 6, 5), (NULL,
             '2012-11-20 00:11:25.417469', NULL, '2012-11-20 00:11:25
             .417481', NULL, NULL, NULL, 0, 1, 7, 6) ON DUPLICATE KEY UPDATE
              `caseversion_id`=VALUES(`caseversion_id`),
              `run_id`=VALUES(`run_id`), `cc_version`=VALUES(`cc_version`),
              `modified_by_id`=VALUES(`modified_by_id`),
              `modified_on`=VALUES(`modified_on`), `order`=VALUES(`order`)",

        Query 10: In order to add the runcaseversion_environment records,
        we need to
            have all the relevant runcaseversions and prefetch the
            environments for the
            caseversions

            "SELECT `execution_runcaseversion`.`id`,
            `execution_runcaseversion`.`created_on`,
            `execution_runcaseversion`.`created_by_id`,
            `execution_runcaseversion`.`modified_on`,
            `execution_runcaseversion`.`modified_by_id`,
            `execution_runcaseversion`.`deleted_on`,
            `execution_runcaseversion`.`deleted_by_id`,
            `execution_runcaseversion`.`cc_version`,
            `execution_runcaseversion`.`run_id`, `execution_runcaseversion`
            .`caseversion_id`, `execution_runcaseversion`.`order`,
            `library_caseversion`.`id`, `library_caseversion`.`created_on`,
            `library_caseversion`.`created_by_id`, `library_caseversion`
            .`modified_on`, `library_caseversion`.`modified_by_id`,
            `library_caseversion`.`deleted_on`, `library_caseversion`
            .`deleted_by_id`, `library_caseversion`.`cc_version`,
            `library_caseversion`.`status`, `library_caseversion`
            .`productversion_id`, `library_caseversion`.`case_id`,
            `library_caseversion`.`name`, `library_caseversion`
            .`description`, `library_caseversion`.`latest`,
            `library_caseversion`.`envs_narrowed` FROM
            `execution_runcaseversion` INNER JOIN `library_caseversion` ON (
            `execution_runcaseversion`.`caseversion_id` =
            `library_caseversion`.`id`) WHERE (`execution_runcaseversion`
            .`deleted_on` IS NULL AND `execution_runcaseversion`.`run_id` =
            1 ) ORDER BY `execution_runcaseversion`.`order` ASC",

        Query 11: This is the prefetch_related query used with Query 9.  Django
            makes a separate query and links them in-memory.

            "SELECT (`library_caseversion_environments`.`caseversion_id`) AS
             `_prefetch_related_val`, `environments_environment`.`id`,
             `environments_environment`.`created_on`,
             `environments_environment`.`created_by_id`,
             `environments_environment`.`modified_on`,
             `environments_environment`.`modified_by_id`,
             `environments_environment`.`deleted_on`,
             `environments_environment`.`deleted_by_id`,
             `environments_environment`.`cc_version`,
             `environments_environment`.`profile_id` FROM
             `environments_environment` INNER JOIN
             `library_caseversion_environments` ON (
             `environments_environment`.`id` =
             `library_caseversion_environments`.`environment_id`) WHERE (
             `environments_environment`.`deleted_on` IS NULL AND
             `library_caseversion_environments`.`caseversion_id` IN (2, 3,
             4, 5, 6, 7))",

        Query 12: runcaseversion_environments that already existed that
        pertain to
            the runcaseversions that are still relevant.

            "SELECT `execution_runcaseversion_environments`
            .`runcaseversion_id`, `execution_runcaseversion_environments`
            .`environment_id` FROM `execution_runcaseversion_environments`
            WHERE `execution_runcaseversion_environments`
            .`runcaseversion_id` IN (3, 4, 5, 2, 6, 7)",

        Query 13: Get the environments for this run so we can find the
        intersection
            with the caseversions.

            "SELECT `environments_environment`.`id` FROM
            `environments_environment` INNER JOIN
            `execution_run_environments` ON (`environments_environment`.`id`
             = `execution_run_environments`.`environment_id`) WHERE (
             `environments_environment`.`deleted_on` IS NULL AND
             `execution_run_environments`.`run_id` = 1 )",

        Query 14: Find the runcaseversion_environments that are no longer
        relevant.

            "SELECT `execution_runcaseversion_environments`.`id`,
            `execution_runcaseversion_environments`.`runcaseversion_id`,
            `execution_runcaseversion_environments`.`environment_id` FROM
            `execution_runcaseversion_environments`
            WHERE ((`execution_runcaseversion_environments`.`runcaseversion_id`
            = 2  AND `execution_runcaseversion_environments`.`environment_id`
            = 5 ))",

        Query 15: Delete the runcaseversion_environments that pertained to the
            caseversion that are no longer relevant.

            "DELETE FROM `execution_runcaseversion_environments` WHERE `id`
            IN (9)",

        Query 16: Bulk insert of runcaseversion_environment mappings.

            "INSERT INTO `execution_runcaseversion_environments`
            (`runcaseversion_id`, `environment_id`) VALUES (7, 3), (5, 4),
            (3, 1), (3, 3), (6, 4), (7, 4), (5, 2), (6, 1), (4, 4), (3, 2),
            (7, 1), (6, 3), (6, 2), (4, 3), (4, 2), (3, 4), (5, 1), (4, 1),
            (7, 2), (5, 3)",

        Query 17: Update the test run to make it active.

            "UPDATE `execution_run` SET `created_on` = '2012-11-20 00:11:25',
            `created_by_id` = NULL, `modified_on` = '2012-11-20 00:11:25',
            `modified_by_id` = NULL, `deleted_on` = NULL, `deleted_by_id` =
            NULL, `cc_version` = 1, `has_team` = 0, `status` = 'active',
            `productversion_id` = 1, `name` = 'Test Run', `description` = '',
            `start` = '2012-11-19', `end` = NULL, `build` = NULL,
            `is_series` = 0, `series_id` = NULL
            WHERE (`execution_run`.`deleted_on` IS NULL
            AND `execution_run`.`id` = 1
            AND `execution_run`.`cc_version` = 0 )"

        """

        r = self.F.RunFactory.create(productversion=self.pv8)

        # one that should get deleted because it's not in the suite
        old_cv = self.F.CaseVersionFactory.create(
            name="I shouldn't be here",
            productversion=self.pv8,
            status="active",
            )
        self.F.RunCaseVersionFactory(run=r, caseversion=old_cv)

        # test suite add to run
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        # cases that belong to the suite
        cv_needed = []
        for num in range(6):
            cv = self.F.CaseVersionFactory.create(
                name="casey" + str(num),
                productversion=self.pv8,
                status="active",
                )
            self.F.SuiteCaseFactory.create(suite=ts, case=cv.case)
            cv_needed.append(cv)

        # existing one that we should keep
        existing_rcv = self.F.RunCaseVersionFactory(run=r,
            caseversion=cv_needed[3],
            order=0,
            )
        # existing env that should be removed in removal phase
        old_env = self.F.EnvironmentFactory.create_set(
            ["OS", "Browser"],
            ["Atari", "RS-232"],
            )[0]
        self.F.model.RunCaseVersion.environments.through(
            runcaseversion=existing_rcv,
            environment=old_env,
            ).save()

        from django.conf import settings
        from django.db import connection

        settings.DEBUG = True
        connection.queries = []

        try:
            with self.assertNumQueries(16):
                r.activate()

            # to debug, uncomment these lines:
#            import json
#            r.activate()
#            print(json.dumps([x["sql"] for x in connection.queries], indent=4))
#            print("NumQueries={0}".format(len(connection.queries)))

            selects = [x["sql"] for x in connection.queries if x["sql"].startswith("SELECT")]
            inserts = [x["sql"] for x in connection.queries if x["sql"].startswith("INSERT")]
            updates = [x["sql"] for x in connection.queries if x["sql"].startswith("UPDATE")]
            deletes = [x["sql"] for x in connection.queries if x["sql"].startswith("DELETE")]

            self.assertEqual(len(selects), 10)
            self.assertEqual(len(inserts), 2)
            self.assertEqual(len(updates), 1)
            self.assertEqual(len(deletes), 3)
        except AssertionError as e:
            raise e
        finally:
            settings.DEBUG = False

        self.refresh(r)

        self.assertEqual(r.runcaseversions.count(), 6)
        self.assertEqual(
            self.F.model.RunCaseVersion.environments.through.objects.count(),
            24,
            )
        self.assertEqual(
            self.F.model.RunCaseVersion.objects.filter(
            run=r,
            caseversion=old_cv,
            ).count(), 0)


    def test_run_refresh(self):
        """
        Refresh the runcaseversions while the run remains active

        Very similar to previous test case, but this all happens while the
        run is in active state.  Ensuring that it has the same end-result.

        """
        r = self.F.RunFactory.create(
            productversion=self.pv8)

        r.activate()

        # one that should get deleted because it's no longer in the suite
        old_cv = self.F.CaseVersionFactory.create(
            name="I shouldn't be here",
            productversion=self.pv8,
            status="active",
            )
        self.F.RunCaseVersionFactory(run=r, caseversion=old_cv)

        # test suite add to run
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        # cases that belong to the suite
        cv_needed = []
        for num in range(6):
            cv = self.F.CaseVersionFactory.create(
                name="casey" + str(num),
                productversion=self.pv8,
                status="active",
                )
            self.F.SuiteCaseFactory.create(suite=ts, case=cv.case)
            cv_needed.append(cv)

        # existing one that we should keep
        existing_rcv = self.F.RunCaseVersionFactory(
            run=r,
            caseversion=cv_needed[3],
            order=0,
            )
        # existing env that should be removed in removal phase
        old_env = self.F.EnvironmentFactory.create_set(
            ["OS", "Browser"],
            ["Atari", "RS-232"],
            )[0]
        self.F.model.RunCaseVersion.environments.through(
            runcaseversion=existing_rcv,
            environment=old_env,
            ).save()

        r.refresh()

        self.refresh(r)

        self.assertEqual(r.runcaseversions.count(), 6)
        self.assertEqual(
            self.F.model.RunCaseVersion.environments.through.objects.count(),
            24,
            )
        self.assertEqual(self.F.model.RunCaseVersion.objects.filter(
                run=r,
                caseversion=old_cv,
                ).count(), 0)


    def test_run_refresh_draft_no_op(self):
        """Refresh the runcaseversions on draft run is no op."""
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

        r.refresh()

        self.assertEqual(r.runcaseversions.count(), 1)
        self.assertEqual(
            self.model.Result.objects.filter(runcaseversion__run=r).count(), 1)
        self.assertEqual(
            self.model.Result.objects.count(), 1)



class RefreshTransactionTest(case.TransactionTestCase):
    """Tests for ``Importer`` transactional behavior."""

    def setUp(self):
        """Set up envs, product and product versions used by all tests."""
        self.envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"], "Browser": ["Firefox", "Chrome"]})
        self.p = self.F.ProductFactory.create()
        self.pv8 = self.F.ProductVersionFactory.create(
            product=self.p, version="8.0", environments=self.envs)
        self.pv9 = self.F.ProductVersionFactory.create(
            product=self.p, version="9.0", environments=self.envs)


    def create_run_needing_refresh(self):
        """
        Refresh the runcaseversions while the run remains active

        Very similar to previous test case, but this all happens while the
        run is in active state.  Ensuring that it has the same end-result.

        """
        r = self.F.RunFactory.create(
            productversion=self.pv8)

        r.activate()

        # one that should get deleted because it's no longer in the suite
        deleteme_cv = self.F.CaseVersionFactory.create(
            name="I shouldn't be here",
            productversion=self.pv8,
            status="active",
            )
        # adds runcaseversion.environments (4 of them), too
        self.F.RunCaseVersionFactory(run=r, caseversion=deleteme_cv)

        # add suite to run
        ts = self.F.SuiteFactory.create(product=self.p, status="active")
        self.F.RunSuiteFactory.create(suite=ts, run=r)

        # add 6 cases to suite, needed by the run
        cv_needed = []
        for num in range(6):
            cv = self.F.CaseVersionFactory.create(
                name="casey" + str(num),
                productversion=self.pv8,
                status="active",
                )
            self.F.SuiteCaseFactory.create(suite=ts, case=cv.case)
            cv_needed.append(cv)

        # existing rcv that we should keep, because it's in the suite
        # also adds runcaseversion.environments here (4 more)
        keepme_rcv = self.F.RunCaseVersionFactory(
            run=r,
            caseversion=cv_needed[3],
            order=0,
            )
        # existing env that should be removed in removal phase
        deleteme_env = self.F.EnvironmentFactory.create_set(
            ["OS", "Browser"],
            ["Atari", "RS-232"],
            )[0]
        self.F.model.RunCaseVersion.environments.through(
            runcaseversion=keepme_rcv,
            environment=deleteme_env,
            ).save()

        return {
            "r": r,
            "deleteme_cv": deleteme_cv,
            "ts": ts,
            "cv_needed": cv_needed,
            "existing_rcv": keepme_rcv,
            "old_env": deleteme_env,
            }


    def assert_rolled_back(self, test_data):
        # refetch the run from the db after changes.
        r = test_data["r"]
        self.refresh(r)

        # should still contain the ``deleteme_cv`` and the
        self.assertEqual(r.runcaseversions.count(), 2)
        # 4 for each rcv that remains, plus 1 rogue env we added manually
        self.assertEqual(
            self.F.model.RunCaseVersion.environments.through.objects.count(),
            9,
            )
        self.assertEqual(self.F.model.RunCaseVersion.objects.filter(
            run=r,
            caseversion=test_data["deleteme_cv"],
            ).count(), 1)


    def do_rollback_test(self, new_func):
        """Perform the rollback test with an exception in a new function."""
        test_data = self.create_run_needing_refresh()

        class SurpriseException(RuntimeError):
            pass

        def raise_exception(*args, **kwargs):
            raise SurpriseException("Surprise!")

        new_func.side_effect = raise_exception

        with self.assertRaises(SurpriseException):
            test_data["r"].refresh()

        self.assert_rolled_back(test_data)


    @patch.object(Run, '_delete_runcaseversions')
    def test_exception_in_delete_runcaseversions(self, new_func):
        """
        An unknown exception is thrown:
            * after creating unfresh test data
            * before deleting rcvs
        so the entire transaction is rolled back.
        """
        self.do_rollback_test(new_func)


    @patch.object(Run, '_bulk_insert_new_runcaseversions')
    def test_exception_in_bulk_insert_new_rcv(self, new_func):
        """
        An unknown exception is thrown:
            * after deleting rcvs
            * before bulk insert
        so the entire transaction is rolled back.
        """
        self.do_rollback_test(new_func)


    @patch.object(Run, '_bulk_update_runcaseversion_environments_for_lock')
    def test_exception_in_bulk_update_rcv_envs(self, new_func):
        """
        An unknown exception is thrown:
            * after bulk insert of rcvs
            * before bulk update of envs
        so the entire transaction is rolled back.
        """
        self.do_rollback_test(new_func)


    @patch.object(Run, '_lock_caseversions_complete')
    def test_exception_after_complete(self, new_func):
        """
        An unknown exception is thrown:
            * after bulk update of envs, and everything should be done.
        so the entire transaction is rolled back.
        """
        self.do_rollback_test(new_func)

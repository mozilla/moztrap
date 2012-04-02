"""
Tests for Case and related models (CaseVersion, CaseStep).

"""
from datetime import datetime

from django.core.exceptions import ValidationError

from mock import patch

from tests import case



class CaseTest(case.DBTestCase):
    def test_unicode(self):
        c = self.F.CaseFactory()

        self.assertEqual(unicode(c), u"case #%s" % c.id)


    def test_clone_versions(self):
        """Cloning a case clones all versions."""
        cv = self.F.CaseVersionFactory.create(name="CV 1")

        new = cv.case.clone()

        self.assertEqual(new.versions.get().name, "Cloned: CV 1")


    def test_all_versions(self):
        """Returns ordered product versions paired with caseversion or None."""
        c = self.F.CaseFactory()
        pv1 = self.F.ProductVersionFactory(product=c.product, version="1")
        pv2 = self.F.ProductVersionFactory(product=c.product, version="2")
        pv3 = self.F.ProductVersionFactory(product=c.product, version="3")
        cv2 = self.F.CaseVersionFactory(productversion=pv2, case=c)

        self.assertEqual(
            c.all_versions(), [(pv1, None), (pv2, cv2), (pv3, None)])



class CaseVersionTest(case.DBTestCase):
    def test_unicode(self):
        cv = self.F.CaseVersionFactory(name="Foo")

        self.assertEqual(unicode(cv), u"Foo")


    def test_clone_clones_case(self):
        """Cloning caseversion w/o case or productversion clones case."""
        cv = self.F.CaseVersionFactory(name="one")
        self.F.CaseVersionFactory(case=cv.case)

        new = cv.clone()

        self.assertIsInstance(new, cv.__class__)
        self.assertEqual(
            [v.name for v in new.case.versions.all()], ["Cloned: one"])


    def test_clone_override_name(self):
        """Providing name override prevents 'Cloned: ' prefix."""
        cv = self.F.CaseVersionFactory(name="one")

        new = cv.clone(overrides={"name": "two"})

        self.assertEqual(new.name, "two")


    def test_clone_sets_draft_state(self):
        """Clone of active caseversion is still draft."""
        cv = self.F.CaseVersionFactory(status="active")

        new = cv.clone()

        self.assertEqual(new.status, "draft")


    def test_clone_steps(self):
        """Cloning a caseversion clones its steps."""
        cs = self.F.CaseStepFactory.create()
        pv = self.F.ProductVersionFactory.create(
            product=cs.caseversion.case.product, version="2.0")

        new = cs.caseversion.clone(overrides={"productversion": pv})

        cloned_step = new.steps.get()
        self.assertNotEqual(cloned_step, cs)
        self.assertEqual(cloned_step.instruction, cs.instruction)


    def test_clone_attachments(self):
        """Cloning a caseversion clones its attachments."""
        ca = self.F.CaseAttachmentFactory.create()
        pv = self.F.ProductVersionFactory.create(
            product=ca.caseversion.case.product, version="2.0")

        new = ca.caseversion.clone(overrides={"productversion": pv})

        cloned_attachment = new.attachments.get()
        self.assertNotEqual(cloned_attachment, ca)
        self.assertEqual(
            cloned_attachment.attachment.name, ca.attachment.name)


    def test_clone_tags(self):
        """Cloning a caseversion clones its tag relationships."""
        tag = self.F.TagFactory.create()
        cv = self.F.CaseVersionFactory.create()
        cv.tags.add(tag)
        pv = self.F.ProductVersionFactory.create(
            product=cv.case.product, version="2.0")

        new = cv.clone(overrides={"productversion": pv})

        self.assertEqual(new.tags.get(), tag)


    def test_clone_environments(self):
        """Cloning a CaseVersion clones its environments."""
        cv = self.F.CaseVersionFactory(environments={"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(
            product=cv.case.product, version="2.0")

        new = cv.clone(overrides={"productversion": pv})

        self.assertEqual(len(new.environments.all()), 2)


    def test_default_active(self):
        """New CaseVersion defaults to active state."""
        cv = self.F.CaseVersionFactory()

        self.assertEqual(cv.status, "active")


    def test_gets_productversion_envs(self):
        """A new caseversion inherits environments of its product version."""
        pv = self.F.ProductVersionFactory(environments={"OS": ["Windows", "Linux"]})
        cv = self.F.CaseVersionFactory(productversion=pv)

        self.assertEqual(set(cv.environments.all()), set(pv.environments.all()))
        self.assertFalse(cv.envs_narrowed)


    def test_inherits_env_removal(self):
        """Removing an env from a productversion cascades to caseversion."""
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs)
        cv = self.F.CaseVersionFactory.create(productversion=pv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))
        self.assertFalse(cv.envs_narrowed)


    def test_non_narrowed_inherits_env_addition(self):
        """Adding env to productversion cascades to non-narrowed caseversion."""
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs[1:])
        cv = self.F.CaseVersionFactory.create(productversion=pv, envs_narrowed=False)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs))


    def test_narrowed_does_not_inherit_env_addition(self):
        """Adding env to prodversion doesn't cascade to narrowed caseversion."""
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs[1:])
        cv = self.F.CaseVersionFactory.create(productversion=pv, envs_narrowed=True)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))


    def test_direct_env_narrowing_sets_envs_narrowed(self):
        """Removing an env from a caseversion directly sets envs_narrowed."""
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        cv = self.F.CaseVersionFactory.create(environments=envs)

        self.assertFalse(cv.envs_narrowed)

        cv.remove_envs(envs[0])

        self.assertTrue(self.refresh(cv).envs_narrowed)


    def test_adding_new_version_sets_latest(self):
        """Adding a new case version updates latest version."""
        c = self.F.CaseFactory.create()
        p = c.product
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="3", case=c)

        self.assertEqual(
            [v.latest for v in c.versions.all()],
            [False, False, True]
            )


    def test_deleting_version_sets_latest(self):
        """Deleting a case version updates latest version."""
        c = self.F.CaseFactory.create()
        p = c.product
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        cv = self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="3", case=c)

        cv.delete()

        self.assertEqual(
            [v.latest for v in c.versions.all()],
            [False, True]
            )


    def test_undeleting_version_sets_latest(self):
        """Undeleting a case version updates latest version."""
        c = self.F.CaseFactory.create()
        p = c.product
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        cv = self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="3", case=c)

        cv.delete()
        self.refresh(cv).undelete()

        self.assertEqual(
            [v.latest for v in c.versions.all()],
            [False, False, True]
            )


    @patch("moztrap.model.ccmodel.datetime")
    def test_update_latest_version_does_not_change_modified_on(self, mock_dt):
        """Updating latest case version does not change modified_on."""
        mock_dt.datetime.utcnow.return_value = datetime(2012, 1, 30)
        cv = self.F.CaseVersionFactory.create()

        mock_dt.datetime.utcnow.return_value = datetime(2012, 1, 31)
        cv.case.set_latest_version()

        self.assertEqual(self.refresh(cv).modified_on, datetime(2012, 1, 30))
        self.assertEqual(self.refresh(cv.case).modified_on, datetime(2012, 1, 30))


    def test_update_latest_version_does_not_change_modified_by(self):
        """Updating latest case version does not change modified_by."""
        u = self.F.UserFactory.create()
        c = self.F.CaseFactory.create(user=u)
        cv = self.F.CaseVersionFactory.create(case=c, user=u)

        cv.case.set_latest_version()

        self.assertEqual(self.refresh(cv).modified_by, u)
        self.assertEqual(self.refresh(c).modified_by, u)


    def test_set_latest_instance_being_saved_is_updated(self):
        """Version being saved gets correct latest setting."""
        c = self.F.CaseFactory.create()
        p = c.product
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        cv = self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)

        self.assertEqual(cv.latest, True)


    def test_skip_set_latest(self):
        """Passing skip_set_latest to save skips setting latest version."""
        cv1 = self.F.CaseVersionFactory.create(productversion__version="1")
        pv2 = self.F.ProductVersionFactory.create(
            product=cv1.productversion.product, version="2")
        cv2 = self.model.CaseVersion(case=cv1.case, productversion=pv2)
        cv2.save(skip_set_latest=True)

        # latest attributes are wrong because we didn't update them
        self.assertEqual(self.refresh(cv1).latest, True)
        self.assertEqual(self.refresh(cv2).latest, False)


    def test_latest_version(self):
        """Case.latest_version() gets latest version."""
        c = self.F.CaseFactory.create()
        p = c.product
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)
        self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        cv = self.F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="3", case=c)

        self.assertEqual(c.latest_version(), cv)


    def test_bug_urls(self):
        """bug_urls aggregates bug urls from all results, sans dupes."""
        cv = self.F.CaseVersionFactory.create()
        rcv1 = self.F.RunCaseVersionFactory.create(caseversion=cv)
        rcv2 = self.F.RunCaseVersionFactory.create(caseversion=cv)
        result1 = self.F.ResultFactory.create(runcaseversion=rcv1)
        result2 = self.F.ResultFactory.create(runcaseversion=rcv2)
        self.F.StepResultFactory.create(result=result1)
        self.F.StepResultFactory.create(
            result=result1, bug_url="http://www.example.com/bug1")
        self.F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug1")
        self.F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            cv.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )


    def test_unique_constraint(self):
        """Can't have two versions of a case for same product version."""
        cv = self.F.CaseVersionFactory.create()

        new = self.F.CaseVersionFactory.build(
            productversion=cv.productversion, case=cv.case)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_with_unset_case_and_productversion(self):
        """Uniqueness checking doesn't blow up if case/productversion unset."""
        new = self.model.CaseVersion()

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing object."""
        cv = self.F.CaseVersionFactory.create()

        cv.name = "new name"

        cv.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted version doesn't prevent new with same productversion."""
        cv = self.F.CaseVersionFactory.create()
        cv.delete()

        self.F.CaseVersionFactory.create(
            case=cv.case, productversion=cv.productversion)



class CaseStepTest(case.DBTestCase):
    """Tests for the CaseStep model."""
    def test_unicode(self):
        """Unicode representation is 'step #X'."""
        c = self.F.CaseStepFactory(number=1)

        self.assertEqual(unicode(c), u"step #1")


    def test_unique_constraint(self):
        """Can't have two steps of the same number in one caseversion."""
        cs = self.F.CaseStepFactory.create()

        new = self.F.CaseStepFactory.build(
            caseversion=cs.caseversion, number=cs.number)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_with_unset_caseversion(self):
        """Uniqueness checking doesn't blow up if caseversion unset."""
        new = self.model.CaseStep()

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing step."""
        cs = self.F.CaseStepFactory.create()

        cs.instruction = "new instruction"

        cs.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted step doesn't prevent new with same number."""
        cs = self.F.CaseStepFactory.create()
        cs.delete()

        self.F.CaseStepFactory.create(
            caseversion=cs.caseversion, number=cs.number)



class CaseAttachmentTest(case.DBTestCase):
    """Tests for the CaseAttachment model."""
    def test_unicode(self):
        """Unicode representation is name."""
        ca = self.F.CaseAttachmentFactory(name="afile.txt")

        self.assertEqual(unicode(ca), "afile.txt")


    def test_name(self):
        """``name`` property is basename of attached file name."""
        ca = self.F.CaseAttachmentFactory(name="thefile.txt")

        self.assertEqual(ca.name, "thefile.txt")


    def test_url(self):
        """``url`` property is shortcut to attached file url."""
        ca = self.F.CaseAttachmentFactory()

        self.assertEqual(ca.url, ca.attachment.url)

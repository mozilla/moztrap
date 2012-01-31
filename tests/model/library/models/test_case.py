# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for Case and related models (CaseVersion, CaseStep).

"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from .... import factories as F
from ....utils import refresh



class CaseTest(TestCase):
    def test_unicode(self):
        c = F.CaseFactory()

        self.assertEqual(unicode(c), u"case #%s" % c.id)


    def test_clone_versions(self):
        """Cloning a case clones all versions."""
        cv = F.CaseVersionFactory.create(name="CV 1")

        new = cv.case.clone()

        self.assertEqual(new.versions.get().name, "Cloned: CV 1")


    def test_all_versions(self):
        """Returns ordered product versions paired with caseversion or None."""
        c = F.CaseFactory()
        pv1 = F.ProductVersionFactory(product=c.product, version="1")
        pv2 = F.ProductVersionFactory(product=c.product, version="2")
        pv3 = F.ProductVersionFactory(product=c.product, version="3")
        cv2 = F.CaseVersionFactory(productversion=pv2, case=c)

        self.assertEqual(
            c.all_versions(), [(pv1, None), (pv2, cv2), (pv3, None)])



class CaseVersionTest(TestCase):
    def test_unicode(self):
        cv = F.CaseVersionFactory(name="Foo")

        self.assertEqual(unicode(cv), u"Foo")


    def test_clone_clones_case(self):
        """Cloning caseversion w/o case or productversion clones case."""
        cv = F.CaseVersionFactory(name="one")
        F.CaseVersionFactory(case=cv.case)

        new = cv.clone()

        self.assertIsInstance(new, cv.__class__)
        self.assertEqual(
            [v.name for v in new.case.versions.all()], ["Cloned: one"])


    def test_clone_override_name(self):
        """Providing name override prevents 'Cloned: ' prefix."""
        cv = F.CaseVersionFactory(name="one")

        new = cv.clone(overrides={"name": "two"})

        self.assertEqual(new.name, "two")


    def test_clone_sets_draft_state(self):
        """Clone of active caseversion is still draft."""
        cv = F.CaseVersionFactory(status="active")

        new = cv.clone()

        self.assertEqual(new.status, "draft")


    def test_clone_steps(self):
        """Cloning a caseversion clones its steps."""
        cs = F.CaseStepFactory.create()
        pv = F.ProductVersionFactory.create(
            product=cs.caseversion.case.product, version="2.0")

        new = cs.caseversion.clone(overrides={"productversion": pv})

        cloned_step = new.steps.get()
        self.assertNotEqual(cloned_step, cs)
        self.assertEqual(cloned_step.instruction, cs.instruction)


    def test_clone_attachments(self):
        """Cloning a caseversion clones its attachments."""
        ca = F.CaseAttachmentFactory.create()
        pv = F.ProductVersionFactory.create(
            product=ca.caseversion.case.product, version="2.0")

        new = ca.caseversion.clone(overrides={"productversion": pv})

        cloned_attachment = new.attachments.get()
        self.assertNotEqual(cloned_attachment, ca)
        self.assertEqual(
            cloned_attachment.attachment.name, ca.attachment.name)


    def test_clone_tags(self):
        """Cloning a caseversion clones its tag relationships."""
        tag = F.TagFactory.create()
        cv = F.CaseVersionFactory.create()
        cv.tags.add(tag)
        pv = F.ProductVersionFactory.create(
            product=cv.case.product, version="2.0")

        new = cv.clone(overrides={"productversion": pv})

        self.assertEqual(new.tags.get(), tag)


    def test_clone_environments(self):
        """Cloning a CaseVersion clones its environments."""
        cv = F.CaseVersionFactory(environments={"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(
            product=cv.case.product, version="2.0")

        new = cv.clone(overrides={"productversion": pv})

        self.assertEqual(len(new.environments.all()), 2)


    def test_gets_productversion_envs(self):
        """A new caseversion inherits environments of its product version."""
        pv = F.ProductVersionFactory(environments={"OS": ["Windows", "Linux"]})
        cv = F.CaseVersionFactory(productversion=pv)

        self.assertEqual(set(cv.environments.all()), set(pv.environments.all()))
        self.assertFalse(cv.envs_narrowed)


    def test_inherits_env_removal(self):
        """Removing an env from a productversion cascades to caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs)
        cv = F.CaseVersionFactory.create(productversion=pv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))
        self.assertFalse(cv.envs_narrowed)


    def test_non_narrowed_inherits_env_addition(self):
        """Adding env to productversion cascades to non-narrowed caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        cv = F.CaseVersionFactory.create(productversion=pv, envs_narrowed=False)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs))


    def test_narrowed_does_not_inherit_env_addition(self):
        """Adding env to prodversion doesn't cascade to narrowed caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        cv = F.CaseVersionFactory.create(productversion=pv, envs_narrowed=True)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))


    def test_direct_env_narrowing_sets_envs_narrowed(self):
        """Removing an env from a caseversion directly sets envs_narrowed."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        cv = F.CaseVersionFactory.create(environments=envs)

        self.assertFalse(cv.envs_narrowed)

        cv.remove_envs(envs[0])

        self.assertTrue(refresh(cv).envs_narrowed)


    def test_adding_new_version_sets_latest(self):
        """Adding a new case version updates latest version."""
        c = F.CaseFactory.create()
        p = c.product
        F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)
        F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="3", case=c)

        self.assertEqual(
            [v.latest for v in c.versions.all()],
            [False, False, True]
            )


    def test_instance_being_saved_is_updated(self):
        """Version being saved gets correct latest setting."""
        c = F.CaseFactory.create()
        p = c.product
        F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="1", case=c)
        cv = F.CaseVersionFactory.create(
            productversion__product=p, productversion__version="2", case=c)

        self.assertEqual(cv.latest, True)


    def test_bug_urls(self):
        """bug_urls aggregates bug urls from all results, sans dupes."""
        cv = F.CaseVersionFactory.create()
        rcv1 = F.RunCaseVersionFactory.create(caseversion=cv)
        rcv2 = F.RunCaseVersionFactory.create(caseversion=cv)
        result1 = F.ResultFactory.create(runcaseversion=rcv1)
        result2 = F.ResultFactory.create(runcaseversion=rcv2)
        F.StepResultFactory.create(result=result1)
        F.StepResultFactory.create(
            result=result1, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            cv.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )


    def test_unique_constraint(self):
        """Can't have two versions of a case for same product version."""
        cv = F.CaseVersionFactory.create()

        new = F.CaseVersionFactory.build(
            productversion=cv.productversion, case=cv.case)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing object."""
        cv = F.CaseVersionFactory.create()

        cv.name = "new name"

        cv.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted version doesn't prevent new with same productversion."""
        cv = F.CaseVersionFactory.create()
        cv.delete()

        F.CaseVersionFactory.create(
            case=cv.case, productversion=cv.productversion)



class CaseStepTest(TestCase):
    """Tests for the CaseStep model."""
    def test_unicode(self):
        """Unicode representation is 'step #X'."""
        c = F.CaseStepFactory(number=1)

        self.assertEqual(unicode(c), u"step #1")


    def test_unique_constraint(self):
        """Can't have two steps of the same number in one caseversion."""
        cs = F.CaseStepFactory.create()

        new = F.CaseStepFactory.build(
            caseversion=cs.caseversion, number=cs.number)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing step."""
        cs = F.CaseStepFactory.create()

        cs.instruction = "new instruction"

        cs.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted step doesn't prevent new with same number."""
        cs = F.CaseStepFactory.create()
        cs.delete()

        F.CaseStepFactory.create(
            caseversion=cs.caseversion, number=cs.number)



class CaseAttachmentTest(TestCase):
    """Tests for the CaseAttachment model."""
    def test_unicode(self):
        """Unicode representation is name."""
        ca = F.CaseAttachmentFactory(attachment__name="afile.txt")

        self.assertEqual(unicode(ca), "afile.txt")


    def test_name(self):
        """``name`` property is basename of attached file name."""
        ca = F.CaseAttachmentFactory(attachment__name="thefile.txt")

        self.assertEqual(ca.name, "thefile.txt")


    def test_url(self):
        """``url`` property is shortcut to attached file url."""
        ca = F.CaseAttachmentFactory()

        self.assertEqual(ca.url, ca.attachment.url)

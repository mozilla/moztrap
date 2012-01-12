# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
from django.test import TestCase

from ... import factories as F
from ...utils import refresh



class CaseTest(TestCase):
    def test_unicode(self):
        c = F.CaseFactory()

        self.assertEqual(unicode(c), u"case #%s" % c.id)


    def test_clone_versions(self):
        """Cloning a case clones its latest version only."""
        cv1 = F.CaseVersionFactory.create(
            latest=False, number=1, name="CV 1")
        F.CaseVersionFactory.create(
            latest=True, number=2, name="CV 2", case=cv1.case)

        new = cv1.case.clone()

        self.assertEqual(new.versions.get().name, "Cloned: CV 2")



class CaseVersionTest(TestCase):
    def test_unicode(self):
        c = F.CaseVersionFactory(name="Foo")

        self.assertEqual(unicode(c), u"Foo")


    def test_clone_steps(self):
        """Cloning a caseversion clones its steps."""
        cs = F.CaseStepFactory.create()

        new = cs.caseversion.clone()

        cloned_step = new.steps.get()
        self.assertNotEqual(cloned_step, cs)
        self.assertEqual(cloned_step.instruction, cs.instruction)


    def test_clone_attachments(self):
        """Cloning a caseversion clones its attachments."""
        ca = F.CaseAttachmentFactory.create()

        new = ca.caseversion.clone()

        cloned_attachment = new.attachments.get()
        self.assertNotEqual(cloned_attachment, ca)
        self.assertEqual(
            cloned_attachment.attachment.path, ca.attachment.path)


    def test_clone_tags(self):
        """Cloning a caseversion clones its tag relationships."""
        tag = F.TagFactory.create()
        cv = F.CaseVersionFactory.create()
        cv.tags.add(tag)

        new = cv.clone()

        self.assertEqual(new.tags.get(), tag)


    def test_caseversion_gets_productversion_envs(self):
        """A new caseversion inherits environments of its product version."""
        pv = F.ProductVersionFactory(environments={"OS": ["Windows", "Linux"]})
        cv = F.CaseVersionFactory(productversion=pv)

        self.assertEqual(set(cv.environments.all()), set(pv.environments.all()))
        self.assertFalse(cv.envs_narrowed)


    def test_caseversion_inherits_env_removal(self):
        """Removing an env from a productversion cascades to caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs)
        cv = F.CaseVersionFactory.create(productversion=pv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))
        self.assertFalse(cv.envs_narrowed)


    def test_non_narrowed_caseversion_inherits_env_addition(self):
        """Adding env to productversion cascades to non-narrowed caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        cv = F.CaseVersionFactory.create(productversion=pv, envs_narrowed=False)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs))


    def test_narrowed_caseversion_does_not_inherit_env_addition(self):
        """Adding env to prodversion doesn't cascade to narrowed caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        cv = F.CaseVersionFactory.create(productversion=pv, envs_narrowed=True)

        pv.add_envs(envs[0])

        self.assertEqual(set(cv.environments.all()), set(envs[1:]))


    def test_direct_caseversion_env_narrowing_sets_envs_narrowed(self):
        """Removing an env from a caseversion directly sets envs_narrowed."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        cv = F.CaseVersionFactory.create(environments=envs)

        self.assertFalse(cv.envs_narrowed)

        cv.remove_envs(envs[0])

        self.assertTrue(refresh(cv).envs_narrowed)



class CaseStepTest(TestCase):
    def test_unicode(self):
        c = F.CaseStepFactory(number=1)

        self.assertEqual(unicode(c), u"step #1")

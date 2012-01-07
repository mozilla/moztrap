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

from ...core.builders import create_product
from ...environments.builders import create_environments
from ...tags.builders import create_tag
from ..builders import (
    create_case, create_caseversion, create_casestep, create_caseattachment)



class CaseTest(TestCase):
    @property
    def Case(self):
        from cc.library.models import Case
        return Case


    def test_unicode(self):
        c = create_case()

        self.assertEqual(unicode(c), u"case #%s" % c.id)


    def test_clone_versions(self):
        """Cloning a case clones its latest version only."""
        cv1 = create_caseversion(latest=False, number=1, name="CV 1")
        create_caseversion(latest=True, number=2, name="CV 2", case=cv1.case)

        new = cv1.case.clone()

        self.assertEqual(new.versions.get().name, "Cloned: CV 2")



class CaseVersionTest(TestCase):
    @property
    def CaseVersion(self):
        from cc.library.models import CaseVersion
        return CaseVersion


    def test_unicode(self):
        c = create_caseversion(name="Foo")

        self.assertEqual(unicode(c), u"Foo")


    def test_clone_steps(self):
        """Cloning a caseversion clones its steps."""
        cs = create_casestep()

        new = cs.caseversion.clone()

        cloned_step = new.steps.get()
        self.assertNotEqual(cloned_step, cs)
        self.assertEqual(cloned_step.instruction, cs.instruction)


    def test_clone_attachments(self):
        """Cloning a caseversion clones its attachments."""
        ca = create_caseattachment()

        new = ca.caseversion.clone()

        cloned_attachment = new.attachments.get()
        self.assertNotEqual(cloned_attachment, ca)
        self.assertEqual(
            cloned_attachment.attachment.path, ca.attachment.path)


    def test_clone_tags(self):
        """Cloning a caseversion clones its tag relationships."""
        tag = create_tag()
        cv = create_caseversion()
        cv.tags.add(tag)

        new = cv.clone()

        self.assertEqual(new.tags.get(), tag)


    def test_caseversion_gets_product_envs(self):
        """
        A new test case inherits the environments of its product.

        """
        p = create_product()
        p.environments.add(*create_environments(["OS"], ["Windows"], ["Linux"]))

        cv = create_caseversion(case=create_case(product=p))

        self.assertEqual(set(cv.environments.all()), set(p.environments.all()))
        self.assertEqual(cv.envs_narrowed, False)



class CaseStepTest(TestCase):
    @property
    def CaseStep(self):
        from cc.library.models import CaseStep
        return CaseStep


    def test_unicode(self):
        c = create_casestep(number=1)

        self.assertEqual(unicode(c), u"step #1")

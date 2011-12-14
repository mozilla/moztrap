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

from ..builders import create_case, create_caseversion, create_casestep



class CaseTest(TestCase):
    @property
    def Case(self):
        from cc.library.models import Case
        return Case


    def test_unicode(self):
        c = create_case()

        self.assertEqual(unicode(c), u"case #%s" % c.id)



class CaseVersionTest(TestCase):
    @property
    def CaseVersion(self):
        from cc.library.models import CaseVersion
        return CaseVersion


    def test_unicode(self):
        c = create_caseversion(name="Foo")

        self.assertEqual(unicode(c), u"Foo")



class CaseStepTest(TestCase):
    @property
    def CaseStep(self):
        from cc.library.models import CaseStep
        return CaseStep


    def test_unicode(self):
        c = create_casestep(number=1)

        self.assertEqual(unicode(c), u"step #1")

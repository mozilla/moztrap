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
Tests for Profile model.

"""
from django.test import TestCase

from .... import factories as F

from cc.model.environments.models import Profile



class ProfileTest(TestCase):
    def test_unicode(self):
        """Unicode representation is name."""
        p = F.ProfileFactory(name="Browser Testing Environments")

        self.assertEqual(unicode(p), u"Browser Testing Environments")


    def test_generate(self):
        """Auto-generating cartesian product of given elements."""
        os = F.CategoryFactory(name="Operating System")
        browser = F.CategoryFactory(name="Browser")
        windows = F.ElementFactory(name="Windows", category=os)
        linux = F.ElementFactory(name="Linux", category=os)
        firefox = F.ElementFactory(name="Firefox", category=browser)
        chrome = F.ElementFactory(name="Chrome", category=browser)

        p = Profile.generate("New Profile", windows, linux, firefox, chrome)

        self.assertEqual(p.name, "New Profile")
        self.assertEqual(
            set([unicode(e) for e in p.environments.all()]),
            set(
                [
                    "Firefox, Linux",
                    "Firefox, Windows",
                    "Chrome, Linux",
                    "Chrome, Windows",
                    ]
                )
            )

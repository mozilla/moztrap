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
from tests import case



class ProfileTest(case.DBTestCase):
    def test_unicode(self):
        """Unicode representation is name."""
        p = self.F.ProfileFactory(name="Browser Testing Environments")

        self.assertEqual(unicode(p), u"Browser Testing Environments")


    def test_generate(self):
        """Auto-generating cartesian product of given elements."""
        os = self.F.CategoryFactory(name="Operating System")
        browser = self.F.CategoryFactory(name="Browser")
        windows = self.F.ElementFactory(name="Windows", category=os)
        linux = self.F.ElementFactory(name="Linux", category=os)
        firefox = self.F.ElementFactory(name="Firefox", category=browser)
        chrome = self.F.ElementFactory(name="Chrome", category=browser)

        p = self.model.Profile.generate(
            "New Profile", windows, linux, firefox, chrome)

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


    def test_clone(self):
        """Cloning a profile clones member environments."""
        p = self.F.ProfileFactory.create()
        env = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows"]}, profile=p)[0]

        new = p.clone()

        self.assertEqual(new.environments.count(), 1)
        self.assertNotEqual(new.environments.get(), env)


    def test_categories(self):
        """Categories method returns categories involved in the profile."""
        p = self.F.ProfileFactory.create()
        self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows", "OS X"], "Browser": ["Firefox", "Chrome"]},
            profile=p)

        self.assertEqual(
            [c.name for c in p.categories()], ["Browser", "OS"])

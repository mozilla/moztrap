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
Tests for Category model.

"""
from tests import case



class CategoryTest(case.DBTestCase):
    """Tests for Category model."""
    def test_unicode(self):
        """Unicode representation is name of category."""
        c = self.F.CategoryFactory(name="Operating System")

        self.assertEqual(unicode(c), u"Operating System")


    def test_delete_prevention(self):
        """Deleting category used in an environment raises ProtectedError."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        with self.assertRaises(self.model.ProtectedError):
            el.category.delete()


    def test_delete_prevention_ignores_deleted_envs(self):
        """Can delete category included only in a deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        el.category.delete()

        self.assertFalse(self.refresh(el.category).deleted_on is None)


    def test_deletable(self):
        """deletable property is False if category is included in an env."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        self.assertFalse(el.category.deletable)


    def test_deletable_ignores_deleted_envs(self):
        """deletable property is True if category is in deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        self.assertTrue(el.category.deletable)

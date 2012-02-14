# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Tests for Case Conductor permissions template tags and filters.

"""
from tests import case



class PermissionFilterTest(case.DBTestCase):
    """Tests for permission-related filters."""
    @property
    def permissions(self):
        """The templatetags module under test."""
        from cc.view.templatetags import permissions
        return permissions


    def test_has_perm(self):
        """``has_perm`` filter passes through to user's has_perm method."""
        u = self.F.UserFactory.create(permissions=["library.create_cases"])
        self.assertTrue(self.permissions.has_perm(u, "library.create_cases"))

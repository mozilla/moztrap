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
Tests for CC base admin forms.

"""
from django.test import TestCase

from django.contrib.admin.sites import AdminSite

from ... import factories as F

from cc.core.ccadmin import CCModelForm, TeamModelAdmin
from cc.core.models import ProductVersion



class CCModelFormTest(TestCase):
    """Tests of CCModelForm."""
    def test_commit(self):
        """CCModelForm passes in user when saving model with commit=True."""
        u = F.UserFactory.create()
        p = F.ProductFactory.create(name="Firefox")
        f = CCModelForm(instance=p, data={"name": "Fennec"})

        p = f.save(commit=True, user=u)

        self.assertEqual(p.modified_by, u)


    def test_no_commit(self):
        """CCModelForm patches save() so user is tracked w/ commit=False."""
        u = F.UserFactory.create()
        p = F.ProductFactory.create(name="Firefox")
        f = CCModelForm(instance=p, data={"name": "Fennec"})

        p = f.save(commit=False, user=u)
        p.save()

        self.assertEqual(p.modified_by, u)



class TeamModelAdminTest(TestCase):
    """Tests of TeamModelAdmin."""
    def test_fieldsets(self):
        """Sans declared fieldsets, puts team fields into Team fieldset."""
        ma = TeamModelAdmin(ProductVersion, AdminSite())

        fs = ma.get_fieldsets(None, None)

        self.assertEqual(len(fs), 4)

        default, team, deletion, meta = fs

        self.assertNotIn("has_team", default[1]["fields"])
        self.assertNotIn("own_team", default[1]["fields"])
        self.assertEqual(team[0], "Team")
        self.assertEqual(team[1]["fields"], [("has_team", "own_team")])

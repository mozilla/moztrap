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
Tests for CC base admin forms.

"""
from django.test import TestCase

from ...core.builders import create_product, create_user



class CCModelFormTest(TestCase):
    """Tests of CCModelForm."""
    @property
    def CCModelForm(self):
        from cc.core.ccadmin import CCModelForm
        return CCModelForm


    def test_commit(self):
        """CCModelForm passes in user when saving model with commit=True."""
        u = create_user()
        p = create_product(name="Firefox")
        f = self.CCModelForm(instance=p, data={"name": "Fennec"})

        p = f.save(commit=True, user=u)

        self.assertEqual(p.modified_by, u)


    def test_no_commit(self):
        """CCModelForm patches save() so user is tracked w/ commit=False."""
        u = create_user()
        p = create_product(name="Firefox")
        f = self.CCModelForm(instance=p, data={"name": "Fennec"})

        p = f.save(commit=False, user=u)
        p.save()

        self.assertEqual(p.modified_by, u)

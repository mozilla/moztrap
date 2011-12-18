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
Tests for Product admin.

"""
from ..base import AdminTestCase

from ...core.builders import create_product
from ...utils import refresh



class ProductAdminTest(AdminTestCase):
    app_label = "core"
    model_name = "product"


    def test_changelist(self):
        """Product changelist page loads without error, contains name."""
        create_product(name="Firefox")

        self.get(self.changelist_url).mustcontain("Firefox")


    def test_change_page(self):
        """Product change page loads without error, contains name."""
        p = create_product(name="Firefox")

        self.get(self.change_url(p)).mustcontain("Firefox")


    def test_change_tracks_user(self):
        """Making a change via the admin tracks modified-by user."""
        p = create_product(name="Firefox")
        url = self.change_url(p)
        form = self.get(url).forms[0]
        form["name"] = "Fennec"

        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(refresh(p).modified_by, self.user)


    def test_delete_tracks_user(self):
        """Deletion via the admin tracks deleted-by user."""
        p = create_product(name="Firefox")
        url = self.delete_url(p)
        form = self.get(url).forms[0]

        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_bulk_delete_tracks_user(self):
        """Deletion via bulk-action tracks deleted-by user."""
        p = create_product(name="Firefox")
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "delete"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_bulk_undelete(self):
        """Bulk undelete action works."""
        p = create_product(name="Firefox")
        p.delete()
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "undelete"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0)

        self.assertEqual(refresh(p).deleted_on, None)


    def test_hard_delete(self):
        """Hard deletion via bulk-action really deletes."""
        p = create_product(name="Firefox")
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "delete_selected"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0).forms[0].submit()

        self.assertEqual(p.__class__.objects.count(), 0)

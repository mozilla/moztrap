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
Tests for suite-management forms.

"""
from tests import case



class EditSuiteFormTest(case.DBTestCase):
    """Tests for EditSuiteForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.suites.forms import EditSuiteForm
        return EditSuiteForm


    def test_edit_suite(self):
        """Can edit suite, sets modified-by."""
        s = self.F.SuiteFactory()
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(s.product.id),
                "name": "new name",
                "description": "new desc",
                "status": "draft",
                },
            instance=s,
            user=u)

        suite = f.save()

        self.assertEqual(suite.name, "new name")
        self.assertEqual(suite.description, "new desc")
        self.assertEqual(suite.modified_by, u)


    def test_no_change_product_option(self):
        """No option to change to different product."""
        self.F.ProductFactory.create()
        s = self.F.SuiteFactory()

        f = self.form(instance=s)
        self.assertEqual(
            [c[0] for c in f.fields["product"].choices],
            ['', s.product.id]
            )


    def test_no_edit_product(self):
        """Can't change product"""
        p = self.F.ProductFactory()
        s = self.F.SuiteFactory()

        f = self.form(
            {
                "product": str(p.id),
                "name": "new name",
                "description": "new desc",
                "status": "draft",
                },
            instance=s,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["product"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )



class AddSuiteFormTest(case.DBTestCase):
    """Tests for AddSuiteForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.suites.forms import AddSuiteForm
        return AddSuiteForm


    def test_add_suite(self):
        """Can add suite, has created-by user."""
        p = self.F.ProductFactory()
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(p.id),
                "name": "Foo",
                "description": "foo desc",
                "status": "draft",
                },
            user=u
            )

        suite = f.save()

        self.assertEqual(suite.product, p)
        self.assertEqual(suite.name, "Foo")
        self.assertEqual(suite.description, "foo desc")
        self.assertEqual(suite.created_by, u)

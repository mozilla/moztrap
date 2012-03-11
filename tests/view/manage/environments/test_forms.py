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
Tests for environment forms.

"""
from tests import case



class AddProfileFormTest(case.DBTestCase):
    """Tests for AddProfileForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.environments.forms import AddProfileForm
        return AddProfileForm


    def test_save(self):
        """Given a name and element list, autogenerates a profile."""
        e1 = self.F.ElementFactory.create()
        e2 = self.F.ElementFactory.create()
        self.F.ElementFactory.create()
        u = self.F.UserFactory.create()

        f = self.form(
            {
                "elements": [str(e1.id), str(e2.id)],
                "name": "Foo",
                "cc_version": "0"},
            user=u,
            )
        self.assertTrue(f.is_valid())
        p = f.save()

        self.assertEqual(p.created_by, u)
        self.assertEqual(p.name, "Foo")
        self.assertEqual(
            set(p.environments.get().elements.all()), set([e1, e2]))


    def test_empty_category_rendered(self):
        """A category with no elements is still rendered in elements widget."""
        self.F.CategoryFactory.create(name="EmptyCat")

        self.assertIn("EmptyCat", unicode(self.form()["elements"]))


    def test_elements_rendered(self):
        """Elements are rendered in widget."""
        self.F.ElementFactory.create(name="SomeElement")

        self.assertIn("SomeElement", unicode(self.form()["elements"]))


    def test_selected_element_ids(self):
        """Selected elements are rendered checked."""
        unsel = self.F.ElementFactory.create()
        sel = self.F.ElementFactory.create()

        f = self.form({"elements": [str(sel.id)]})

        rendered = unicode(f["elements"])
        self.assertIn('id="element-{0}">'.format(unsel.id), rendered)
        self.assertIn('id="element-{0}" checked>'.format(sel.id), rendered)

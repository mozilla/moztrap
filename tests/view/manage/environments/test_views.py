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
Tests for environment management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class ProfilesViewTest(case.view.manage.ListViewTestCase,
                       case.view.manage.CCModelListTests,
                       ):
    """Tests for environment profiles manage list."""
    form_id = "manage-profiles-form"
    perm = "manage_environments"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.ProfileFactory


    @property
    def url(self):
        """Shortcut for manage-profiles url."""
        return reverse("manage_profiles")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        p1 = self.factory.create(name="Foo 1")
        p1.environments.add(*envs)
        p2 = self.factory.create(name="Foo 2")
        p2.environments.add(*envs[1:])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Profile 1")
        self.factory.create(name="Profile 2")

        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Profile 2", "Profile 1")



class ProfileDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for profile-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a profile."""
        super(ProfileDetailTest, self).setUp()
        self.profile = self.F.ProfileFactory.create()


    @property
    def url(self):
        """Shortcut for profile detail url."""
        return reverse(
            "manage_profile_details",
            kwargs=dict(profile_id=self.profile.id)
            )


    def test_details_envs(self):
        """Details lists envs."""
        self.profile.environments.add(
            *self.F.EnvironmentFactory.create_full_set({"OS": ["Windows"]}))

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Windows")



class AddProfileTest(case.view.FormViewTestCase):
    """Tests for add profile view."""
    form_id = "profile-add-form"


    @property
    def url(self):
        """Shortcut for add-profile url."""
        return reverse("manage_profile_add")


    def setUp(self):
        """Add manage-environments permission to user."""
        super(AddProfileTest, self).setUp()
        self.add_perm("manage_environments")


    def test_success(self):
        """Can add a profile with basic data."""
        el = self.F.ElementFactory.create()
        form = self.get_form()
        form["name"] = "Foo Profile"
        form["elements"] = [str(el.id)]

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_profiles"))

        res.follow().mustcontain("Profile 'Foo Profile' added.")

        p = self.model.Profile.objects.get()
        self.assertEqual(p.name, "Foo Profile")
        self.assertEqual(p.environments.get().elements.get(), el)


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_environments_permission(self):
        """Requires manage-environments permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)



class CategoryManagementViewTest(case.view.AuthenticatedViewTestCase):
    """
    Tests for adding/editing/deleting categories and elements.

    Currently this is implemented as an AJAX-POST-handling decorator on the
    add-profile view, but it's likely to be split into its own separate view,
    thus the tests are separated.

    """
    # @@@ Since these POSTs are all done by JS rather than by submitting a real
    # form, can't test via the usual WebTest form submission. Could submit a
    # GET request, scrape the CSRF token and submit it with the POST, but
    # doubling the number of requests slows down the tests and gains little.
    csrf_checks = False


    @property
    def url(self):
        """Shortcut to add-profile url."""
        return reverse("manage_profile_add")


    def setUp(self):
        """Add manage-environments permission to user."""
        super(CategoryManagementViewTest, self).setUp()
        self.add_perm("manage_environments")


    def post(self, data, **kwargs):
        """Shortcut for ajax-posting to url, authenticated."""
        headers = kwargs.setdefault("headers", {})
        headers.setdefault("X-Requested-With", "XMLHttpRequest")
        return super(CategoryManagementViewTest, self).post(data, **kwargs)


    def test_ignores_non_ajax(self):
        """Non-ajax requests are passed through."""
        res = self.app.post(self.url, {}, user=self.user)

        self.assertElement(res.html, "form", id="profile-add-form")


    def test_ignores_non_POST(self):
        """Non-POST requests are passed through."""
        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        self.assertElement(res.json["html"], "form", id="profile-add-form")


    def test_no_action(self):
        """Returns empty JSON data if given no action."""
        res = self.post({})

        self.assertEqual(res.json, {"messages": []})


    def test_delete_element(self):
        """Can delete an element."""
        el = self.F.ElementFactory.create()

        res = self.post({"action-delete": "element-{0}".format(el.id)})

        self.assertEqual(res.json, {"messages": [], "html": ""})
        self.assertEqual(self.refresh(el).deleted_by, self.user)


    def test_delete_category(self):
        """Can delete a category."""
        c = self.F.CategoryFactory.create()

        res = self.post({"action-delete": "category-{0}".format(c.id)})

        self.assertEqual(res.json, {"messages": [], "html": ""})
        self.assertEqual(self.refresh(c).deleted_by, self.user)


    def test_delete_bad_obj_type(self):
        """Trying to delete an unknown object type returns no_replace=True."""
        res = self.post({"action-delete": "foo-1"})

        self.assertEqual(res.json, {"messages": [], "no_replace": True})


    def test_delete_bad_obj_id(self):
        """Trying to delete a bad id returns no_replace=True."""
        res = self.post({"action-delete": "element-1"})

        self.assertEqual(res.json, {"messages": [], "no_replace": True})


    def test_add_category(self):
        """Can add a new category."""
        res = self.post({"new-category-name": "FooCat"})

        self.assertElement(
            res.json["html"],
            lambda t: (
                t.name == "h3" and
                t["class"] == "title" and
                t.text == "FooCat"
                )
            )


    def test_blank_category_name(self):
        """Blank category name results in error message, no new HTML."""
        res = self.post({"new-category-name": ""})

        self.assertEqual(
            res.json,
            {
                "no_replace": True,
                "messages": [
                    {
                        "message": "Please enter a category name.",
                        "level": 40,
                        "tags": "error",
                        }
                    ],
                },
            )


    def test_edit_category(self):
        """Can change the name of a category."""
        c = self.F.CategoryFactory.create(name="OldName")

        res = self.post(
            {"new-category-name": "FooCat", "category-id": str(c.id)})

        self.assertElement(
            res.json["html"],
            lambda t: (
                t.name == "h3" and
                t["class"] == "title" and
                t.text == "FooCat"
                )
            )

        self.assertEqual(self.refresh(c).name, "FooCat")


    def test_edit_category_with_elements(self):
        """Editing category with elements preserves element input state."""
        c = self.F.CategoryFactory.create(name="OldName")
        el1 = self.F.ElementFactory.create(category=c)
        el2 = self.F.ElementFactory.create(category=c)

        res = self.post(
            {
                "new-category-name": "FooCat",
                "category-id": str(c.id),
                "elements": [str(el1.id)],
                }
            )

        self.assertElement(
            res.json["html"],
            "input",
            attrs={
                "type": "checkbox",
                "name": "elements",
                "value": str(el1.id),
                "checked": True,
                }
            )

        self.assertElement(
            res.json["html"],
            "input",
            attrs={
                "type": "checkbox",
                "name": "elements",
                "value": str(el2.id),
                "checked": None,
                },
            )


    def test_add_element(self):
        """Can add a new element."""
        c = self.F.CategoryFactory.create()

        res = self.post(
            {"new-element-name": "FooElement", "category-id": str(c.id)})

        label_finder = lambda t: (
            t.name == "label" and
            t.text == "FooElement"
            )

        e = self.model.Element.objects.get()
        self.assertEqual(e.name, "FooElement")
        self.assertEqual(e.category, c)

        self.assertElement(res.json["elem"], label_finder)
        self.assertElement(res.json["preview"], label_finder)
        self.assertElement(
            res.json["elem"],
            "input",
            attrs={
                "type": "checkbox",
                "name": "elements",
                "value": str(e.id),
                "checked": None,
                }
            )


    def test_blank_element_name(self):
        """Blank element name results in error message, no new HTML."""
        res = self.post({"new-element-name": ""})

        self.assertEqual(
            res.json,
            {
                "no_replace": True,
                "messages": [
                    {
                        "message": "Please enter an element name.",
                        "level": 40,
                        "tags": "error",
                        }
                    ],
                },
            )


    def test_edit_element(self):
        """Can change the name of a element."""
        e = self.F.ElementFactory.create(name="OldName")

        res = self.post(
            {"new-element-name": "FooElement", "element-id": str(e.id)})

        label_finder = lambda t: (
                t.name == "label" and
                t.text == "FooElement"
                )

        self.assertElement(res.json["elem"], label_finder)
        self.assertElement(res.json["preview"], label_finder)
        self.assertElement(
            res.json["elem"],
            "input",
            attrs={
                "type": "checkbox",
                "name": "elements",
                "value": str(e.id),
                "checked": None,
                }
            )

        self.assertEqual(self.refresh(e).name, "FooElement")

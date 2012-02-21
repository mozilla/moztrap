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

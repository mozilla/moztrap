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
Tests for Environment admin.

"""
from mock import patch

from tests import case



class EnvironmentAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "environment"


    def test_changelist(self):
        """Environment changelist page loads without error, contains name."""
        self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})

        self.get(self.changelist_url).mustcontain("Linux")


    def test_change_page(self):
        """Environment change page loads without error, contains name."""
        e = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})[0]

        self.get(self.change_url(e)).mustcontain("Linux")


    def test_change_page_element(self):
        """Environment change page includes Element-m2m inline."""
        e = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})[0]

        self.get(self.change_url(e)).mustcontain("Linux")


    def test_add_element_m2m_with_environment(self):
        """Can add elements when creating a new Environment"""
        profile = self.F.ProfileFactory.create()
        element = self.F.ElementFactory.create(name="Linux")

        # patching extra avoids need for JS to add element-m2m
        with patch(
            "cc.model.environments.admin.EnvironmentElementInline.extra", 1):

            form = self.get(self.add_url).forms[0]
            form["profile"] = str(profile.id)
            form["Environment_elements-0-element"] = str(element.id)
            res = form.submit()

        self.assertEqual(res.status_int, 302)

        self.assertEqual(
            profile.environments.get(
                ).elements.get().name, "Linux")

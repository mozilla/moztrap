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
Tests for runtests forms.

"""
from django.test import TestCase

from ... import factories as F



class EnvironmentSelectionFormTest(TestCase):
    """Tests for environment selection form."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.runtests.forms import EnvironmentSelectionForm
        return EnvironmentSelectionForm


    @property
    def model(self):
        """The models."""
        from cc import model
        return model


    def test_no_extra_arguments(self):
        """By default, form has no environments."""
        f = self.form()

        # only choice is the blank one
        self.assertEqual(
            [c[0] for c in f.fields["environment"].choices], [""])


    def test_environments(self):
        """Can pass in queryset of environments."""
        F.EnvironmentFactory.create_full_set({"OS": ["Linux", "Windows"]})

        f = self.form(environments=self.model.Environment.objects.all())

        # blank choice plus two environments
        choices = list(f.fields["environment"].choices)
        self.assertEqual(len(choices), 3, choices)


    def test_current(self):
        """Can pass in ID of current environment."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})

        f = self.form(
            environments=self.model.Environment.objects.all(),
            current=envs[0].id)

        self.assertEqual(f.initial, {"environment": envs[0].id})


    def test_save(self):
        """Save method returns ID of selected environment."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})

        f = self.form(
            {"environment": str(envs[0].id)},
            environments=self.model.Environment.objects.all())

        self.assertTrue(f.is_valid())
        self.assertEqual(f.save(), envs[0].id)


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
        """By default, form has no fields."""
        f = self.form()

        self.assertEqual(len(f.fields), 0)


    def test_environments(self):
        """Can pass in queryset of environments."""
        F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        cat = self.model.Category.objects.get()

        form = self.form(environments=self.model.Environment.objects.all())

        self.assertEqual(
            dict(
                (fname, [c[1] for c in f.choices])
                for fname, f in form.fields.items()
                ),
            {"category_{0}".format(cat.id): ["Linux", "Windows"]}
            )


    def test_current(self):
        """Can pass in ID of current environment."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        cat = self.model.Category.objects.get()

        f = self.form(
            environments=self.model.Environment.objects.all(),
            current=envs[0].id)

        self.assertEqual(
            f.initial,
            {"category_{0}".format(cat.id): envs[0].elements.get().id}
            )


    def test_bad_current(self):
        """ID of nonexistent environment is ignored."""
        f = self.form(current="-1")

        self.assertEqual(f.initial, {})


    def test_save(self):
        """Save method returns ID of selected environment."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        cat = self.model.Category.objects.get()

        f = self.form(
            {"category_{0}".format(cat.id): str(envs[0].elements.get().id)},
            environments=self.model.Environment.objects.all())

        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.save(), envs[0].id)


    def test_invalid_environment(self):
        """Form validation error if invalid combination is selected."""
        F.EnvironmentFactory.create_set(
            ["OS", "Browser"], ["OS X", "Safari"], ["Windows", "IE"])
        windows = self.model.Element.objects.get(name="Windows")
        safari = self.model.Element.objects.get(name="Safari")

        f = self.form(
            {
                "category_{0}".format(windows.category.id): str(windows.id),
                "category_{0}".format(safari.category.id): str(safari.id),
                },
            environments=self.model.Environment.objects.all()
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors,
            {
                "__all__": [
                    "The selected environment is not valid for this test run. "
                    "Please select a different combination."
                    ]
                }
            )

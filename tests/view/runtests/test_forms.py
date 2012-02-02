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
            {"OS": ["Linux", "Windows"], "Browser": ["Opera", "Firefox"]})
        os = self.model.Category.objects.get(name="OS")
        browser = self.model.Category.objects.get(name="Browser")

        form = self.form(environments=self.model.Environment.objects.all())

        self.assertEqual(
            dict(
                (fname, [c[1] for c in f.choices])
                for fname, f in form.fields.items()
                ),
            {
                "category_{0}".format(browser.id): ["Firefox", "Opera"],
                "category_{0}".format(os.id): ["Linux", "Windows"],
                },
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


    def test_superset_env(self):
        """Selecting a superset of the envs for a valid combo is valid."""
        os = F.CategoryFactory.create(name="OS")
        browser = F.CategoryFactory.create(name="Browser")
        language = F.CategoryFactory.create(name="Language")

        windows = F.ElementFactory.create(name="Windows", category=os)
        linux = F.ElementFactory.create(name="Linux", category=os)
        firefox = F.ElementFactory.create(name="Firefox", category=browser)
        opera = F.ElementFactory.create(name="Opera", category=browser)
        english = F.ElementFactory.create(name="English", category=language)
        spanish = F.ElementFactory.create(name="Spanish", category=language)

        # we only care about language for Opera/Linux, not Firefox/Windows
        winff = F.EnvironmentFactory.create()
        winff.elements.add(windows, firefox)
        linuxoperaenglish = F.EnvironmentFactory.create()
        linuxoperaenglish.elements.add(linux, opera, english)
        linuxoperaspanish = F.EnvironmentFactory.create()
        linuxoperaspanish.elements.add(linux, opera, spanish)

        f = self.form(
            {
                "category_{0}".format(browser.id): str(firefox.id),
                "category_{0}".format(language.id): str(spanish.id),
                "category_{0}".format(os.id): str(windows.id),
                },
            environments=self.model.Environment.objects.all())

        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.save(), winff.id)


    def test_incomplete_env(self):
        """A valid combo that does not include all categories is ok."""
        os = F.CategoryFactory.create(name="OS")
        browser = F.CategoryFactory.create(name="Browser")
        language = F.CategoryFactory.create(name="Language")

        windows = F.ElementFactory.create(name="Windows", category=os)
        linux = F.ElementFactory.create(name="Linux", category=os)
        firefox = F.ElementFactory.create(name="Firefox", category=browser)
        opera = F.ElementFactory.create(name="Opera", category=browser)
        english = F.ElementFactory.create(name="English", category=language)
        F.ElementFactory.create(name="Spanish", category=language)

        winff = F.EnvironmentFactory.create()
        winff.elements.add(windows, firefox)
        linuxoperaenglish = F.EnvironmentFactory.create()
        linuxoperaenglish.elements.add(linux, opera, english)

        f = self.form(
            {
                "category_{0}".format(browser.id): str(firefox.id),
                "category_{0}".format(language.id): "",
                "category_{0}".format(os.id): str(windows.id),
                },
            environments=self.model.Environment.objects.all())

        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.save(), winff.id)

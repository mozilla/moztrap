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
Forms for test execution.

"""
import floppyforms as forms

from ... import model



class EnvironmentSelectionForm(forms.Form):
    """Form for selecting an environment."""
    def __init__(self, *args, **kwargs):
        """Accepts ``environments`` queryset and ``current`` env id."""
        environments = kwargs.pop("environments", [])
        current = kwargs.pop("current", None)

        super(EnvironmentSelectionForm, self).__init__(*args, **kwargs)

        # list of categories, ordered by name
        self.categories = []

        # maps category to list of elements
        self.elements_by_category = {}

        # maps environment ID to list of element IDs, ordered by category
        self.elementids_by_envid = {}

        # elements in current environment
        current_elements = []

        env_element_through_model = model.Environment.elements.through
        env_element_relationships = env_element_through_model.objects.filter(
            environment__in=environments).select_related()

        # first construct the ordered list of categories (and current elements)
        cat_set = set()
        for ee in env_element_relationships:
            cat_set.add(ee.element.category)
            if ee.environment.id == current:
                current_elements.append(ee.element)
        self.categories = sorted(cat_set, key=lambda c: c.name)

        num_categories = len(self.categories)

        # populate elements by category and environment
        for ee in env_element_relationships:
            byenv = self.elementids_by_envid.setdefault(
                ee.environment.id, [None] * num_categories)
            category_index = self.categories.index(ee.element.category)
            byenv[category_index] = ee.element.id

            bycat = self.elements_by_category.setdefault(
                ee.element.category, [])
            bycat.append(ee.element)

        # construct choice-field for each env type
        for category in self.categories:
            self.fields["category_{0}".format(category.id)] = forms.ChoiceField(
                choices=[
                    (e.id, e.name) for e in sorted(
                        self.elements_by_category[category],
                        key=lambda e: e.name)
                    ],
                label=category.name)

        # set initial data based on current user environment
        for element in current_elements:
            field_name = "category_{0}".format(element.category.id)
            self.initial[field_name] = element.id


    def clean(self):
        """Validate that selected elements form valid environment."""
        selected_element_ids = set(
            [int(eid) for eid in self.cleaned_data.itervalues()])
        matches = [
            envid for envid, element_ids in self.elementids_by_envid.items()
            if selected_element_ids == set(element_ids)
            ]
        if not matches:
            raise forms.ValidationError(
                "The selected environment is not valid for this test run. "
                "Please select a different combination.")

        self.cleaned_data["environment"] = matches[0]

        return self.cleaned_data


    def save(self):
        """Return id of selected environment."""
        return self.cleaned_data["environment"]

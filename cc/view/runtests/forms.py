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

        # maps (cat.id, cat.name) to element list for that category.
        # e.g. (1, "Operating System") => [(5, "Windows"), (6, "Linux")]
        self.categories = {}

        # maps environment ID to set of element IDs
        self.envsets = {}

        for env in environments:
            element_ids = set()
            for element in env.elements.select_related("category"):
                element_ids.add(element.id)
                cat = element.category
                options = self.categories.setdefault((cat.id, cat.name), set())
                options.add((element.id, element.name))
            self.envsets[env.id] = element_ids

        # construct choice-field for each env type
        for (catid, catname), options in sorted(
                self.categories.items(), key=lambda x: x[0][1]):
            self.fields["category_{0}".format(catid)] = forms.ChoiceField(
                choices=sorted(options, key=lambda x: x[1]),
                label=catname)

        # set initial data based on current user environment
        if current is not None:
            try:
                environment = model.Environment.objects.get(pk=current)
            except model.Environment.DoesNotExist:
                pass
            else:
                for element in environment.elements.select_related("category"):
                    field_name = "category_{0}".format(element.category.id)
                    self.initial[field_name] = element.id


    def clean(self):
        """Validate that selected elements form valid environment."""
        element_ids = set([int(eid) for eid in self.cleaned_data.itervalues()])
        matches = [
            envid for envid, envset in self.envsets.items()
            if element_ids == envset
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

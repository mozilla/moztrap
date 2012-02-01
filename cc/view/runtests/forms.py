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
    environment = forms.ModelChoiceField(model.Environment.objects.none())


    def __init__(self, *args, **kwargs):
        """Accepts ``environments`` iterable and ``current`` env id."""
        environments = kwargs.pop("environments", None)
        current = kwargs.pop("current", None)

        super(EnvironmentSelectionForm, self).__init__(*args, **kwargs)

        if environments is not None:
            self.fields["environment"].queryset = environments
        if current is not None:
            self.initial["environment"] = current


    def save(self):
        """Return id of selected environment."""
        return self.cleaned_data["environment"].id

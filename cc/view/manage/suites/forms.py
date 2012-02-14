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
Management forms for suites.

"""
import floppyforms as forms

from cc import model
from cc.view.lists import filters
from cc.view.utils import ccforms



class SuiteForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for adding/editing suites."""
    cases = ccforms.CCModelMultipleChoiceField(
        queryset=model.Case.objects.all(),
        required=False,
        widget=ccforms.FilteredSelectMultiple(
            choice_template="manage/suite/case_select/_case_select_item.html",
            listordering_template=(
                "manage/suite/case_select/_case_select_listordering.html"),
            filters=[
                filters.ChoicesFilter(
                    "status", choices=model.CaseVersion.STATUS),
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "tag", lookup="tags", queryset=model.Tag.objects.all()),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
        )

    class Meta:
        model = model.Suite
        fields = ["product", "name", "description", "status"]
        widgets = {
            "product": forms.Select,
            "name": forms.TextInput,
            "description": ccforms.BareTextarea,
            "status": forms.Select,
            }


    def __init__(self, *args, **kwargs):
        """Initialize SuiteForm; set product choices."""
        super(SuiteForm, self).__init__(*args, **kwargs)

        self.fields["product"].queryset = model.Product.objects.all()



class AddSuiteForm(SuiteForm):
    """Form for adding a suite."""
    pass



class EditSuiteForm(SuiteForm):
    """Form for editing a suite."""
    def __init__(self, *args, **kwargs):
        """Initialize EditSuiteForm; no changing product."""
        super(EditSuiteForm, self).__init__(*args, **kwargs)

        pf = self.fields["product"]
        pf.queryset = pf.queryset.filter(pk=self.instance.product_id)

        self.initial["cases"] = list(
            self.instance.cases.values_list("id", flat=True))

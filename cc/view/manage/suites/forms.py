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



class CasesFilteredSelectMultiple(ccforms.FilteredSelectMultiple):
    choice_template_name = "forms/widgets/_select_cases_item.html"


case_filters = [
    filters.ChoicesFilter(
        "status", choices=model.CaseVersion.STATUS),
    filters.KeywordFilter("name"),
    filters.ModelFilter(
        "tag", lookup="tags", queryset=model.Tag.objects.all()),
    filters.ModelFilter(
        "author", queryset=model.User.objects.all()),
    ]



def formfield_callback(f, **kwargs):
    if f.name == "cases":
        kwargs["form_class"] = ccforms.CCModelMultipleChoiceField
    return f.formfield(**kwargs)



class SuiteForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for adding/editing suites."""
    formfield_callback = formfield_callback


    class Meta:
        model = model.Suite
        fields = ["product", "name", "description", "status", "cases"]
        widgets = {
            "product": forms.Select,
            "name": forms.TextInput,
            "description": ccforms.BareTextarea,
            "status": forms.Select,
            "cases": CasesFilteredSelectMultiple(filters=case_filters),
            }


    def __init__(self, *args, **kwargs):
        """Initialize SuiteForm; set product choices."""
        super(SuiteForm, self).__init__(*args, **kwargs)

        self.fields["product"].queryset = model.Product.objects.all()



class AddSuiteForm(SuiteForm):
    """Form for adding a suite."""
     # @@@ Django bug; shouldn't have to specify this for every subclass
    formfield_callback = formfield_callback



class EditSuiteForm(SuiteForm):
    """Form for editing a suite."""
     # @@@ Django bug; shouldn't have to specify this for every subclass
    formfield_callback = formfield_callback


    def __init__(self, *args, **kwargs):
        """Initialize EditSuiteForm; no changing product."""
        super(EditSuiteForm, self).__init__(*args, **kwargs)

        pf = self.fields["product"]
        pf.queryset = pf.queryset.filter(pk=self.instance.product_id)

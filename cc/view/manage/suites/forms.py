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
        choice_attrs=ccforms.product_id_attrs,
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
    product = ccforms.CCModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})

    class Meta:
        model = model.Suite
        fields = ["product", "name", "description", "status"]
        widgets = {
            "name": forms.TextInput,
            "description": ccforms.BareTextarea,
            "status": forms.Select,
            }


    def save(self):
        """Save the suite and case associations."""
        suite = super(SuiteForm, self).save()

        suite.suitecases.all().delete()
        for i, case in enumerate(self.cleaned_data["cases"]):
            model.SuiteCase.objects.create(suite=suite, case=case, order=i)

        return suite



class AddSuiteForm(SuiteForm):
    """Form for adding a suite."""
    pass



class EditSuiteForm(SuiteForm):
    """Form for editing a suite."""
    def __init__(self, *args, **kwargs):
        """Initialize EditSuiteForm; no changing product."""
        super(EditSuiteForm, self).__init__(*args, **kwargs)

        # for suites with cases in them, product is readonly and case options
        # are filtered to that product
        if self.instance.cases.exists():
            pf = self.fields["product"]
            pf.queryset = pf.queryset.filter(pk=self.instance.product_id)
            pf.readonly = True

            cf = self.fields["cases"]
            cf.queryset = cf.queryset.filter(product=self.instance.product_id)

        self.initial["cases"] = list(
            self.instance.cases.values_list("id", flat=True))

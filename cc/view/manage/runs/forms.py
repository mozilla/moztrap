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
Management forms for runs.

"""
import floppyforms as forms

from cc import model
from cc.view.lists import filters
from cc.view.utils import ccforms




class RunForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for adding/editing runs."""
    suites = ccforms.CCModelMultipleChoiceField(
        queryset=model.Suite.objects.all(),
        required=False,
        choice_attrs=ccforms.product_id_attrs,
        widget=ccforms.FilteredSelectMultiple(
            choice_template="manage/run/suite_select/_suite_select_item.html",
            listordering_template=(
                "manage/run/suite_select/_suite_select_listordering.html"),
            filters=[
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
        )
    productversion = ccforms.CCModelChoiceField(
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=ccforms.product_id_attrs)


    class Meta:
        model = model.Run
        fields = ["productversion", "name", "description", "start", "end"]
        widgets = {
            "name": forms.TextInput,
            "description": ccforms.BareTextarea,
            "start": forms.DateInput,
            "end": forms.DateInput,
            }



class AddRunForm(RunForm):
    """Form for adding a run."""
    pass



class EditRunForm(RunForm):
    """Form for editing a run."""
    def __init__(self, *args, **kwargs):
        """Initialize EditRunForm; no changing product version of active run."""
        super(EditRunForm, self).__init__(*args, **kwargs)

        pvf = self.fields["productversion"]
        if self.instance.status == model.Run.STATUS.active:
            # can't change the product version of an active run.
            pvf.queryset = pvf.queryset.filter(
                pk=self.instance.productversion_id)
            pvf.readonly = True
            # can't change suites of an active run either
            self.fields["suites"].readonly = True
        else:
            # regardless, can't switch to different product entirely
            pvf.queryset = pvf.queryset.filter(
                product=self.instance.productversion.product)

        self.initial["suites"] = list(
            self.instance.suites.values_list("id", flat=True))

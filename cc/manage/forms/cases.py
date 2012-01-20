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
Management forms for cases.

"""
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory, BaseInlineFormSet

import floppyforms as forms

from ...core import ccforms
from ...core.models import Product, ProductVersion
from ...library.models import (
    Case, CaseVersion, CaseStep, CaseAttachment, Suite, SuiteCase)
from ...tags.models import Tag



def product_id_attrs(obj):
    return {"data-product-id": obj.product.id}



class AddCaseForm(ccforms.NonFieldErrorsClassFormMixin, forms.Form):
    product = ccforms.CCModelChoiceField(
        Product.objects.all(), choice_attrs=lambda p: {"data-product-id": p.id})
    productversion = ccforms.CCModelChoiceField(
        ProductVersion.objects.all(), choice_attrs=product_id_attrs)
    and_later_versions = forms.BooleanField(initial=True, required=False)
    name = forms.CharField(max_length=200)
    description = forms.CharField(required=False, widget=ccforms.BareTextarea)
    # @@@ tags and attachments aren't proper fields/widgets (yet)
    # these are just placeholder fields for the JS autocomplete stuff, we don't
    # use their contents
    add_tags = forms.CharField(
        widget=ccforms.AutocompleteInput(
            url=lambda: reverse("manage_tags_autocomplete")),
        required=False) # @@@
    add_attachment = forms.FileField(required=False)


    def __init__(self, *args, **kwargs):
        """Initialize AddCaseForm, including StepFormSet."""
        user = kwargs.pop("user")

        super(AddCaseForm, self).__init__(*args, **kwargs)

        self.fields["add_tags"].widget.attrs["data-allow-new"] = (
            "true" if user.has_perm("tags.manage_tags") else "false")
        if user.has_perm("library.manage_suite_cases"):
            self.fields["initial_suite"] = ccforms.CCModelChoiceField(
                Suite.objects.all(),
                choice_attrs=product_id_attrs,
                required=False)
        self.steps_formset = StepFormSet(data=self.data or None, prefix="steps")


    def is_valid(self):
        return self.steps_formset.is_valid() and super(
            AddCaseForm, self).is_valid()


    def clean(self):
        productversion = self.cleaned_data.get("productversion")
        initial_suite = self.cleaned_data.get("initial_suite")
        product = self.cleaned_data.get("product")
        if product and productversion and productversion.product != product:
            raise forms.ValidationError(
                "Must select a version of the correct product.")
        if product and initial_suite and initial_suite.product != product:
            raise forms.ValidationError(
                "Must select a suite for the correct product.")
        return self.cleaned_data


    def save(self):
        data = self.cleaned_data.copy()
        case = Case.objects.create(product=data.pop("product"))
        data["case"] = case

        del data["add_tags"]
        del data["add_attachment"]

        initial_suite = data.pop("initial_suite")
        if initial_suite:
            SuiteCase.objects.create(case=case, suite=initial_suite)

        productversions = [data.pop("productversion")]
        if data.pop("and_later_versions"):
            productversions.extend(ProductVersion.objects.filter(
                    order__gt=productversions[0].order))

        for productversion in productversions:
            this_data = data.copy()
            this_data["productversion"] = productversion
            caseversion = CaseVersion.objects.create(**this_data)
            steps_formset = StepFormSet(
                data=self.data, prefix="steps", instance=caseversion)
            steps_formset.save()
            self._save_tags(caseversion)
            self._save_attachments(caseversion)

        return case


    def _save_tags(self, caseversion):
        # @@@ convert into a modelmultiplechoicefield widget?
        tag_ids = set([int(tid) for tid in self.data.getlist("tag-tag")])
        new_tags = self.data.getlist("tag-newtag")

        for name in new_tags:
            t, created = Tag.objects.get_or_create(
                name=name, product=caseversion.case.product)
            tag_ids.add(t.id)

        current_tag_ids = set([t.id for t in caseversion.tags.all()])
        caseversion.tags.add(*tag_ids.difference(current_tag_ids))
        caseversion.tags.remove(*current_tag_ids.difference(tag_ids))


    def _save_attachments(self, caseversion):
        # @@@ convert into a modelmultiplechoicefield widget?
        delete_ids = set(self.data.getlist("remove-attachment"))
        caseversion.attachments.filter(id__in=delete_ids).delete()

        if self.files: # if no files, it's a plain dict, has no getlist
            for uf in self.files.getlist("add_attachment"):
                CaseAttachment.objects.create(
                    attachment=uf,
                    caseversion=caseversion,
                    )



class StepForm(ccforms.NonFieldErrorsClassFormMixin, forms.ModelForm):
    class Meta:
        model = CaseStep
        widgets = {
            "instruction": ccforms.BareTextarea,
            "expected": ccforms.BareTextarea,
            }
        fields = ["caseversion", "instruction", "expected"]



class BaseStepInlineFormSet(BaseInlineFormSet):
    """Step formset that assigns sequential numbers to steps."""
    def save_new(self, form, commit=True):
        """Assign auto-incrementing step numbers to steps when saving."""
        obj = form.save(commit=False)

        obj.number = self._get_next_step_number()

        if commit:
            obj.save()
        return obj


    def save_existing(self, form, commit=True):
        """Assign auto-incrementing step numbers to steps when saving."""
        obj = form.save(commit=False)

        obj.number = self._get_next_step_number()

        if commit:
            obj.save()
        return obj


    def _get_next_step_number(self):
        """Provide the next step number in sequence."""
        number = getattr(self, "_next_step_number", 1)
        self._next_step_number = number + 1
        return number




StepFormSet = inlineformset_factory(
    CaseVersion,
    CaseStep,
    form=StepForm,
    formset=BaseStepInlineFormSet,
    extra=1)

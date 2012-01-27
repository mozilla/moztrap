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

from .... import model

from ...utils import ccforms




def product_id_attrs(obj):
    return {"data-product-id": obj.product.id}


class CaseVersionForm(ccforms.NonFieldErrorsClassFormMixin, forms.Form):
    """Base form class for AddCaseForm and EditCaseVersionForm."""
    name = forms.CharField(max_length=200)
    description = forms.CharField(required=False, widget=ccforms.BareTextarea)
    status = forms.CharField(
        widget=forms.Select(choices=model.CaseVersion.STATUS))
    # @@@ tags and attachments aren't proper fields/widgets (yet)
    # these are just placeholder fields for the JS autocomplete stuff, we don't
    # use their contents
    add_tags = forms.CharField(
        widget=ccforms.AutocompleteInput(
            url=lambda: reverse("manage_tags_autocomplete")),
        required=False)
    add_attachment = forms.FileField(required=False)


    def __init__(self, *args, **kwargs):
        """Initialize CaseVersionForm, including StepFormSet."""
        self.user = kwargs.pop("user", None)

        super(CaseVersionForm, self).__init__(*args, **kwargs)

        self.fields["add_tags"].widget.attrs["data-allow-new"] = (
            "true"
            if (self.user and self.user.has_perm("tags.manage_tags"))
            else "false"
            )

        self.steps_formset = StepFormSet(
            data=self.data or None, instance=getattr(self, "instance", None))


    def is_valid(self):
        return self.steps_formset.is_valid() and super(
            CaseVersionForm, self).is_valid()


    def save_tags(self, caseversion):
        # @@@ convert into a modelmultiplechoicefield widget?
        tag_ids = set([int(tid) for tid in self.data.getlist("tag-tag")])
        new_tags = self.data.getlist("tag-newtag")

        for name in new_tags:
            # @@@ should pass in user here, need CCQuerySet.get_or_create
            t, created = model.Tag.objects.get_or_create(
                name=name, product=caseversion.case.product)
            tag_ids.add(t.id)

        current_tag_ids = set([t.id for t in caseversion.tags.all()])
        caseversion.tags.add(*tag_ids.difference(current_tag_ids))
        caseversion.tags.remove(*current_tag_ids.difference(tag_ids))


    def save_attachments(self, caseversion):
        # @@@ convert into a modelmultiplechoicefield widget?
        delete_ids = set(self.data.getlist("remove-attachment"))
        caseversion.attachments.filter(id__in=delete_ids).delete()

        if self.files: # if no files, it's a plain dict, has no getlist
            for uf in self.files.getlist("add_attachment"):
                model.CaseAttachment.objects.create(
                    attachment=uf,
                    caseversion=caseversion,
                    user=self.user,
                    )



class AddCaseForm(CaseVersionForm):
    """Form for adding a new single case and some number of versions."""
    product = ccforms.CCModelChoiceField(
        model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})
    productversion = ccforms.CCModelChoiceField(
        model.ProductVersion.objects.all(), choice_attrs=product_id_attrs)
    and_later_versions = forms.BooleanField(initial=True, required=False)


    def __init__(self, *args, **kwargs):
        """Initialize AddCaseForm; possibly add initial_suite field."""
        super(AddCaseForm, self).__init__(*args, **kwargs)

        if self.user and self.user.has_perm("library.manage_suite_cases"):
            self.fields["initial_suite"] = ccforms.CCModelChoiceField(
                model.Suite.objects.all(),
                choice_attrs=product_id_attrs,
                required=False)


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
        assert self.is_valid()

        version_kwargs = self.cleaned_data.copy()
        product = version_kwargs.pop("product")
        case = model.Case.objects.create(product=product, user=self.user)
        version_kwargs["case"] = case
        version_kwargs["user"] = self.user

        del version_kwargs["add_tags"]
        del version_kwargs["add_attachment"]

        initial_suite = version_kwargs.pop("initial_suite", None)
        if initial_suite:
            model.SuiteCase.objects.create(
                case=case, suite=initial_suite, user=self.user)

        productversions = [version_kwargs.pop("productversion")]
        if version_kwargs.pop("and_later_versions"):
            productversions.extend(product.versions.filter(
                    order__gt=productversions[0].order))

        for productversion in productversions:
            this_version_kwargs = version_kwargs.copy()
            this_version_kwargs["productversion"] = productversion
            caseversion = model.CaseVersion.objects.create(
                **this_version_kwargs)
            steps_formset = StepFormSet(
                data=self.data, instance=caseversion, user=self.user)
            steps_formset.save()
            self.save_tags(caseversion)
            self.save_attachments(caseversion)

        return case



class AddBulkCaseForm(AddCaseForm):
    pass # @@@



class EditCaseVersionForm(CaseVersionForm):
    """Form for editing a case version."""
    def __init__(self, *args, **kwargs):
        """Initialize EditCaseVersionForm, pulling instance from kwargs."""
        self.instance = kwargs.pop("instance", None)

        initial = kwargs.setdefault("initial", {})
        initial["name"] = self.instance.name
        initial["description"] = self.instance.description
        initial["status"] = self.instance.status

        super(EditCaseVersionForm, self).__init__(*args, **kwargs)


    def save(self):
        """Save the edited caseversion."""
        assert self.is_valid()

        version_kwargs = self.cleaned_data.copy()
        del version_kwargs["add_tags"]
        del version_kwargs["add_attachment"]

        for k, v in version_kwargs.items():
            setattr(self.instance, k, v)

        self.instance.save(force_update=True)

        self.save_tags(self.instance)
        self.save_attachments(self.instance)

        return self.instance



class StepForm(ccforms.NonFieldErrorsClassFormMixin, forms.ModelForm):
    class Meta:
        model = model.CaseStep
        widgets = {
            "instruction": ccforms.BareTextarea,
            "expected": ccforms.BareTextarea,
            }
        fields = ["caseversion", "instruction", "expected"]



class BaseStepInlineFormSet(BaseInlineFormSet):
    """Step formset that assigns sequential numbers to steps."""
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        if kwargs.get("instance") is not None:
            self.extra = 0
        super(BaseStepInlineFormSet, self).__init__(*args, **kwargs)


    def save_new(self, form, commit=True):
        """Assign auto-incrementing step numbers to steps when saving."""
        obj = form.save(commit=False)

        obj.number = self._get_next_step_number()

        if commit:
            obj.save(user=self.user)
        return obj


    def save_existing(self, form, commit=True):
        """Assign auto-incrementing step numbers to steps when saving."""
        obj = form.save(commit=False)

        obj.number = self._get_next_step_number()

        if commit:
            obj.save(user=self.user)
        return obj


    def _get_next_step_number(self):
        """Provide the next step number in sequence."""
        number = getattr(self, "_next_step_number", 1)
        self._next_step_number = number + 1
        return number




StepFormSet = inlineformset_factory(
    model.CaseVersion,
    model.CaseStep,
    form=StepForm,
    formset=BaseStepInlineFormSet,
    extra=1)

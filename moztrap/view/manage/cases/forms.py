"""
Management forms for cases.

"""
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Max
import floppyforms as forms

from .... import model

from ...utils import mtforms


class BaseCaseForm(mtforms.NonFieldErrorsClassFormMixin, forms.Form):
    """
    Base form for all test case/version forms.

    Provides self.user, tags and status fields, and non-field-errors-class
    mixin.

    """
    status = forms.CharField(
        widget=forms.Select(choices=model.CaseVersion.STATUS),
        initial=model.CaseVersion._meta.get_field("status").default,
        )
    add_tags = forms.CharField(
        widget=mtforms.AutocompleteInput(
            url=lambda: reverse("manage_tags_autocomplete")),
        required=False)
    idprefix = forms.CharField(max_length=200, required=False)


    def __init__(self, *args, **kwargs):
        """Initialize form; pull out user from kwargs, set up data-allow-new."""
        self.user = kwargs.pop("user", None)

        super(BaseCaseForm, self).__init__(*args, **kwargs)

        self.fields["add_tags"].widget.attrs["data-allow-new"] = (
            "true"
            if (self.user and self.user.has_perm("tags.manage_tags"))
            else "false"
            )


    def clean(self):
        """Can't create new tags without appropriate permissions."""
        if (self.data.get("tag-newtag") and
                not (self.user and self.user.has_perm("tags.manage_tags"))):
            raise forms.ValidationError(
                "You do not have permission to create new tags.")
        return self.cleaned_data


    def save_new_tags(self, product=None):
        """Save new tags and add them to the list of tags to assign."""
        tags = self.cleaned_data.setdefault("tags", set())
        tags.update([int(tid) for tid in self.data.getlist("tag-tag")])

        new_tags = self.data.getlist("tag-newtag")

        for name in new_tags:
            # @@@ should pass in user here, need MTQuerySet.get_or_create
            t, created = model.Tag.objects.get_or_create(
                name=name, product=product)
            tags.add(t.id)


    def save_tags(self, caseversion):
        """Update set of tags assigned to ``caseversion``."""
        tags = self.cleaned_data.get("tags", set())

        current_tags = set([t.id for t in caseversion.tags.all()])
        caseversion.tags.add(*tags.difference(current_tags))
        caseversion.tags.remove(*current_tags.difference(tags))



class BaseCaseVersionForm(forms.Form):
    """Base form class for AddCaseForm and EditCaseVersionForm."""
    name = forms.CharField(max_length=200)
    description = forms.CharField(required=False, widget=mtforms.BareTextarea)

    add_attachment = forms.FileField(required=False)


    def __init__(self, *args, **kwargs):
        """Initialize BaseCaseVersionForm, including StepFormSet."""
        super(BaseCaseVersionForm, self).__init__(*args, **kwargs)

        self.steps_formset = StepFormSet(
            data=self.data or None,
            instance=getattr(self, "instance", None),
            )


    def is_valid(self):
        """The form and the steps formset must both be valid."""
        return self.steps_formset.is_valid() and super(
            BaseCaseVersionForm, self).is_valid()


    def save_attachments(self, caseversion):
        # @@@ convert into a modelmultiplechoicefield widget?
        delete_ids = set(self.data.getlist("remove-attachment"))
        caseversion.attachments.filter(id__in=delete_ids).delete()

        if self.files:  # if no files, it's a plain dict, has no getlist
            for uf in self.files.getlist("add_attachment"):
                model.CaseAttachment.objects.create(
                    attachment=uf,
                    name=uf.name,
                    caseversion=caseversion,
                    user=self.user,
                    )


class BaseAddCaseForm(forms.Form):
    """Base form for adding cases."""
    product = mtforms.MTModelChoiceField(
        model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id},
        )
    productversion = mtforms.MTModelChoiceField(
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=mtforms.product_id_attrs,
        label_from_instance=lambda pv: pv.version,
        )
    and_later_versions = forms.BooleanField(initial=True, required=False)


    def __init__(self, *args, **kwargs):
        """Initialize form; possibly add suite field."""
        super(BaseAddCaseForm, self).__init__(*args, **kwargs)

        if self.user and self.user.has_perm("library.manage_suite_cases"):
            self.fields["suite"] = mtforms.MTModelChoiceField(
                model.Suite.objects.all(),
                choice_attrs=mtforms.product_id_attrs,
                required=False)


    def clean(self):
        """Verify that products all match up."""
        productversion = self.cleaned_data.get("productversion")
        suite = self.cleaned_data.get("suite")
        product = self.cleaned_data.get("product")
        if product and productversion and productversion.product != product:
            raise forms.ValidationError(
                "Must select a version of the correct product.")
        if product and suite and suite.product != product:
            raise forms.ValidationError(
                "Must select a suite for the correct product.")
        return self.cleaned_data



class AddCaseForm(BaseAddCaseForm, BaseCaseVersionForm, BaseCaseForm):
    """Form for adding a new single case and some number of versions."""
    def clean(self):
        """
        Call clean methods from parent classes explicitly.

        Can't use super() as forms.Form.clean doesn't.

        """
        # we should get cleaned-data from return value of these, but we know
        # they don't modify self.cleaned_data
        BaseCaseForm.clean(self)
        BaseAddCaseForm.clean(self)
        return self.cleaned_data


    def save(self):
        """Create new case and all called-for versions."""
        assert self.is_valid()

        version_kwargs = self.cleaned_data.copy()
        product = version_kwargs.pop("product")
        idprefix = version_kwargs.pop("idprefix")

        self.save_new_tags(product)

        case = model.Case.objects.create(
            product=product,
            user=self.user,
            idprefix=idprefix,
            )

        version_kwargs["case"] = case
        version_kwargs["user"] = self.user

        del version_kwargs["add_tags"]
        del version_kwargs["add_attachment"]

        suite = version_kwargs.pop("suite", None)
        if suite:
            order = model.SuiteCase.objects.filter(
                suite=suite,
                ).aggregate(Max("order"))["order__max"] or 0
            model.SuiteCase.objects.create(
                case=case,
                suite=suite,
                user=self.user,
                order=order + 1,
                )

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
                data=self.data, instance=caseversion)
            steps_formset.save(user=self.user)
            self.save_tags(caseversion)
            self.save_attachments(caseversion)

        return case



class AddBulkCaseForm(BaseAddCaseForm, BaseCaseForm):
    """Form for adding test cases in bulk."""
    cases = forms.CharField(widget=mtforms.BareTextarea)


    def clean_cases(self):
        """Validate the bulk cases text."""
        data = model.BulkParser().parse(self.cleaned_data["cases"])

        for d in data:
            if "error" in d:
                raise forms.ValidationError(d["error"])

        return data



    def clean(self):
        """
        Call clean methods from parent classes explicitly.

        Can't use super() as forms.Form.clean doesn't.

        """
        # we should get cleaned-data from return value of these, but we know
        # they don't modify self.cleaned_data
        BaseCaseForm.clean(self)
        BaseAddCaseForm.clean(self)

        return self.cleaned_data


    def save(self):
        """Create and return the new case(s) and version(s)."""
        assert self.is_valid()

        product = self.cleaned_data["product"]
        idprefix = self.cleaned_data["idprefix"]

        self.save_new_tags(product)

        productversions = [self.cleaned_data["productversion"]]
        if self.cleaned_data.get("and_later_versions"):
            productversions.extend(product.versions.filter(
                    order__gt=productversions[0].order))

        suite = self.cleaned_data.get("suite")

        cases = []

        order = 0
        if suite:
            order = model.SuiteCase.objects.filter(
                suite=suite,
                ).aggregate(Max("order"))["order__max"] or 0

        for case_data in self.cleaned_data["cases"]:
            case = model.Case.objects.create(
                product=product,
                user=self.user,
                idprefix=idprefix,
                )

            version_kwargs = case_data.copy()
            steps_data = version_kwargs.pop("steps")

            version_kwargs["case"] = case
            version_kwargs["status"] = self.cleaned_data["status"]
            version_kwargs["user"] = self.user

            if suite:
                order += 1
                model.SuiteCase.objects.create(
                    case=case,
                    suite=suite,
                    user=self.user,
                    order=order,
                    )

            for productversion in productversions:
                this_version_kwargs = version_kwargs.copy()
                this_version_kwargs["productversion"] = productversion
                caseversion = model.CaseVersion.objects.create(
                    **this_version_kwargs)
                for i, step_kwargs in enumerate(steps_data, 1):
                    model.CaseStep.objects.create(
                        user=self.user,
                        caseversion=caseversion,
                        number=i,
                        **step_kwargs)
                self.save_tags(caseversion)

            cases.append(case)

        return cases



class EditCaseVersionForm(mtforms.SaveIfValidMixin,
                          BaseCaseVersionForm,
                          BaseCaseForm,
                          ):
    """Form for editing a case version."""
    cc_version = forms.IntegerField(widget=forms.HiddenInput)


    def __init__(self, *args, **kwargs):
        """Initialize EditCaseVersionForm, pulling instance from kwargs."""
        self.instance = kwargs.pop("instance", None)

        initial = kwargs.setdefault("initial", {})
        initial["name"] = self.instance.name
        initial["description"] = self.instance.description
        initial["status"] = self.instance.status
        initial["cc_version"] = self.instance.cc_version

        initial["idprefix"] = self.instance.case.idprefix

        super(EditCaseVersionForm, self).__init__(*args, **kwargs)


    def save(self, user=None):
        """Save the edited caseversion."""
        user = user or self.user
        assert self.is_valid()

        version_kwargs = self.cleaned_data.copy()
        del version_kwargs["add_tags"]
        del version_kwargs["add_attachment"]

        idprefix = version_kwargs.pop("idprefix")

        for k, v in version_kwargs.items():
            setattr(self.instance, k, v)

        if self.instance.case.idprefix != idprefix:
            self.instance.case.idprefix = idprefix
            self.instance.case.save(force_update=True)

        self.instance.save(force_update=True)

        self.save_new_tags(self.instance.case.product)
        self.save_tags(self.instance)
        self.save_attachments(self.instance)
        self.steps_formset.save(user=user)

        return self.instance



class StepForm(mtforms.NonFieldErrorsClassFormMixin, forms.ModelForm):
    class Meta:
        model = model.CaseStep
        widgets = {
            "instruction": mtforms.BareTextarea,
            "expected": mtforms.BareTextarea,
            }
        fields = ["caseversion", "instruction", "expected"]



class BaseStepFormSet(BaseInlineFormSet):
    """Step formset that assigns sequential numbers to steps."""
    def __init__(self, *args, **kwargs):
        if kwargs.get("instance") is not None:
            self.extra = 0
        super(BaseStepFormSet, self).__init__(*args, **kwargs)


    def save(self, user=None):
        """Save all forms in this formset."""
        assert self.is_valid()

        to_delete = set([o.pk for o in self.get_queryset()])

        steps = []
        existing = []
        new = []
        for i, form in enumerate(self.forms, 1):
            step = form.save(commit=False)
            step.number = i
            steps.append(step)
            if step.pk:
                to_delete.remove(step.pk)
                existing.append(step)
            else:
                new.append(step)

        # first delete any existing steps that weren't in the incoming data,
        # then update existing steps on a first pass, then save new steps. This
        # dance is so we never fall afoul of the number-unique constraint (and
        # MySQL's inability to defer constraint checks)
        self.model._base_manager.filter(pk__in=to_delete).delete()

        for step in existing:
            step.save(user=user, force_update=True)

        for step in new:
            step.save(user=user, force_insert=True)

        return steps


    def initial_form_count(self):
        """
        Consider all forms 'extra' when bound so ModelFormSet won't look up PK.

        We don't know that the extra forms are at the end, they could be in any
        order, so Django's "i < self.initial_form_count()" checks are
        inherently broken.

        """
        if self.is_bound:
            return 0
        return super(BaseStepFormSet, self).initial_form_count()


    def _construct_form(self, i, **kwargs):
        """Set empty_permitted and instance for all forms."""
        kwargs["empty_permitted"] = False

        if self.is_bound:
            pk_key = "{0}-id".format(self.add_prefix(i))
            try:
                pk = int(self.data.get(pk_key))
            except (ValueError, TypeError):
                pk = None
            if pk:
                kwargs["instance"] = self._existing_object(pk)
            if kwargs.get("instance") is None:
                self.data[pk_key] = ""

        return super(BaseStepFormSet, self)._construct_form(i, **kwargs)





StepFormSet = inlineformset_factory(
    model.CaseVersion,
    model.CaseStep,
    form=StepForm,
    formset=BaseStepFormSet,
    can_order=False,    # we don't use Django's implementation of
    can_delete=False,   # formset deletion or ordering
    extra=1)

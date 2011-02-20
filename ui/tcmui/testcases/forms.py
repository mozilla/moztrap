from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

from ..environments.forms import EnvironmentConstraintFormSet
from ..environments.models import EnvironmentGroupList

from .models import TestCaseVersion, TestCaseList, TestCaseStep


class TestCaseForm(forms.Form):
    name = forms.CharField()
    product = forms.ChoiceField(choices=[])
    tags = forms.CharField(required=False)


    def __init__(self, *args, **kwargs):
        products = kwargs.pop("products", [])
        super(TestCaseForm, self).__init__(*args, **kwargs)

        self.products = {}
        choices = []
        for p in products:
            choices.append((p.id, p.name))
            self.products[p.id] = p
        self.fields["product"].choices = choices
        self.auth = products.auth

        self.steps_formset = StepFormSet(
            *args, **dict(kwargs, prefix="steps"))
        self.env_formset = EnvironmentConstraintFormSet(
            *args,
            **dict(
                kwargs,
                groups=EnvironmentGroupList.ours(auth=products.auth),
                prefix="environments"
            )
        )


    def is_valid(self):
        return (
            self.steps_formset.is_valid() and
            self.env_formset.is_valid() and
            super(TestCaseForm, self).is_valid()
            )


    def clean(self):
        # @@@ ignoring tags field
        if all([k in self.cleaned_data for k in ["name", "product"]]):
            testcase = TestCaseVersion(
                name=self.cleaned_data["name"],
                product=self.products[self.cleaned_data["product"]],
                maxAttachmentSizeInMbytes = 0, # @@@
                maxNumberOfAttachments = 0, # @@@
                description = "" # @@@
                )
            try:
                TestCaseList.get(auth=self.auth).post(testcase)
            except TestCaseList.Conflict, e:
                if e.response_error == "duplicate.name":
                    self._errors["name"] = self.error_class(
                        ["This name is already in use."])
                else:
                    raise forms.ValidationError(
                        'Unknown conflict "%s"; please correct and try again.'
                        % e.response_error)
            else:
                self.testcase = testcase
        return self.cleaned_data


    def save(self):
        self.steps_formset.save(self.testcase)
        self.env_formset.save(self.testcase)

        return self.testcase



class StepForm(forms.Form):
    instruction = forms.CharField(widget=forms.Textarea)
    expected_result = forms.CharField(widget=forms.Textarea)


    def __init__(self, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        # undo default rows and cols attrs
        self.fields["instruction"].widget.attrs = {}
        self.fields["expected_result"].widget.attrs = {}
        self.empty_permitted = False


    def save(self, testcaseversion, stepnumber):
        step = TestCaseStep(
            name="step %s" % stepnumber, # @@@
            instruction=self.cleaned_data["instruction"],
            expectedResult=self.cleaned_data["expected_result"],
            testCaseVersion=testcaseversion,
            stepNumber=stepnumber,
            estimatedTimeInMin=0 # @@@
            )

        testcaseversion.steps.post(step)



class BaseStepFormSet(BaseFormSet):
    def save(self, testcaseversion):
        for i, form in enumerate(self.forms):
            form.save(testcaseversion, i + 1)


    def _get_empty_form(self, **kwargs):
        # work around http://code.djangoproject.com/ticket/15349
        kwargs["data"] = None
        kwargs["files"] = None
        return super(BaseStepFormSet, self)._get_empty_form(**kwargs)
    empty_form = property(_get_empty_form)





StepFormSet = formset_factory(StepForm, formset=BaseStepFormSet)

from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

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

        self.steps_formset = StepFormSet(*args, **kwargs)


    def is_valid(self):
        return (
            super(TestCaseForm, self).is_valid() and
            self.steps_formset.is_valid()
            )


    def save(self):
        # @@@ ignoring tags field
        testcase = TestCaseVersion(
            name=self.cleaned_data["name"],
            product=self.products[self.cleaned_data["product"]],
            maxAttachmentSizeInMbytes = 0, # @@@
            maxNumberOfAttachments = 0, # @@@
            description = "" # @@@
            )

        TestCaseList.get(auth=self.auth).post(testcase)

        self.steps_formset.save(testcase)

        return testcase



class StepForm(forms.Form):
    instruction = forms.CharField(widget=forms.Textarea)
    expected_result = forms.CharField(widget=forms.Textarea)


    def __init__(self, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        # undo default rows and cols attrs
        self.fields["instruction"].widget.attrs = {}
        self.fields["expected_result"].widget.attrs = {}


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



StepFormSet = formset_factory(StepForm, formset=BaseStepFormSet)

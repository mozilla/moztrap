from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

from ..core import forms as tcmforms

from .models import TestCaseStep



class StepForm(tcmforms.NonFieldErrorsClassFormMixin, forms.Form):
    instruction = forms.CharField(widget=tcmforms.BareTextarea)
    expected_result = forms.CharField(widget=tcmforms.BareTextarea)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", {})
            initial["instruction"] = self.instance.instruction
            initial["expected_result"] = self.instance.expectedResult

        super(StepForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False


    def save(self, testcaseversion, stepnumber):
        info = dict(
            instruction=self.cleaned_data["instruction"],
            expectedResult=self.cleaned_data["expected_result"],
            stepNumber=stepnumber,
            )

        if self.instance is not None:
            for k, v in info.iteritems():
                setattr(self.instance, k, v)
            self.instance.put()
        else:
            step = TestCaseStep(
                **dict(
                    info,
                    name="step %s" % stepnumber, # @@@
                    testCaseVersion=testcaseversion,
                    estimatedTimeInMin=0 # @@@
                    ))

            testcaseversion.steps.post(step)



class BaseStepFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        if instance is not None:
            self.instances = list(instance.steps)
            # just need the initial data to trigger form creation, StepForm
            # will handle actually filling in the data.
            kwargs["initial"] = [{} for i in self.instances]
            self.extra = 0
        else:
            self.instances = []

        super(BaseStepFormSet, self).__init__(*args, **kwargs)


    def save(self, testcaseversion):
        for i, form in enumerate(self.forms):
            form.save(testcaseversion, i + 1)
        for extra_step in self.instances[i+1:]:
            extra_step.delete()


    def _construct_form(self, i, **kwargs):
        try:
            kwargs["instance"] = self.instances[i]
        except:
            pass
        return super(BaseStepFormSet, self)._construct_form(i, **kwargs)


    def _get_empty_form(self, **kwargs):
        # work around http://code.djangoproject.com/ticket/15349
        kwargs["data"] = None
        kwargs["files"] = None
        return super(BaseStepFormSet, self)._get_empty_form(**kwargs)
    empty_form = property(_get_empty_form)



StepFormSet = formset_factory(StepForm, formset=BaseStepFormSet)

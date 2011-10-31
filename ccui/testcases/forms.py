# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

from ..core import forms as ccforms

from .models import TestCaseStep



class StepForm(ccforms.NonFieldErrorsClassFormMixin, forms.Form):
    instruction = forms.CharField(widget=ccforms.BareTextarea)
    expected_result = forms.CharField(widget=ccforms.BareTextarea)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", {})
            initial["instruction"] = self.instance.instruction
            initial["expected_result"] = self.instance.expectedResult

        super(StepForm, self).__init__(*args, **kwargs)


    def save(self, testcaseversion, stepnumber, as_new=False):
        info = dict(
            instruction=self.cleaned_data["instruction"],
            expectedResult=self.cleaned_data["expected_result"],
            stepNumber=stepnumber,
            )

        if self.instance is not None and not as_new:
            for k, v in info.iteritems():
                setattr(self.instance, k, v)
            self.instance.put()
        else:
            step = TestCaseStep(
                **dict(
                    info,
                    name="case %s step %s" % (testcaseversion.id, stepnumber),
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


    def save(self, testcaseversion, as_new=False):
        for i, form in enumerate(self.forms):
            if form.empty_permitted and not form.has_changed():
                break
            form.save(testcaseversion, i + 1, as_new=as_new)
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

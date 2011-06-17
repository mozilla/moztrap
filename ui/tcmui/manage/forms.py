import floppyforms as forms

from ..core import forms as tcmforms
from ..environments.forms import EnvConstrainedAddEditForm

from ..testcases.forms import StepFormSet
from ..testcases.models import (
    TestSuite, TestSuiteList, TestCaseVersion, TestCaseList)
from ..testexecution.models import (
    TestCycle, TestCycleList, TestRun, TestRunList)



def product_id_attrs(obj):
    return {"data-product-id": obj.product.id}



class TestCycleForm(EnvConstrainedAddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=tcmforms.BareTextarea)
    product = tcmforms.ModelChoiceField()
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)
    team = tcmforms.ModelMultipleChoiceField(required=False)


    no_edit_fields = ["product"]
    field_mapping = {
        "start_date": "startDate",
        "end_date": "endDate"}
    assign_later = ["team"]
    entryclass = TestCycle
    listclass = TestCycleList
    parent_name = "product"
    extra_creation_data = {
        "communityAccessAllowed": True,
        "communityAuthoringAllowed": True,
        }



class TestRunForm(EnvConstrainedAddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=tcmforms.BareTextarea)
    test_cycle = tcmforms.ModelChoiceField(
        option_attrs=product_id_attrs)
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)
    team = tcmforms.ModelMultipleChoiceField(required=False)
    suites = tcmforms.ModelMultipleChoiceField(
        required=False, option_attrs=product_id_attrs)


    no_edit_fields = ["test_cycle"]
    field_mapping = {
        "test_cycle": "testCycle",
        "start_date": "startDate",
        "end_date": "endDate"}
    assign_later = ["team", "suites"]
    entryclass = TestRun
    listclass = TestRunList
    parent_name = "testCycle"
    extra_creation_data = {
        "selfAssignLimit": 0,
        "selfAssignAllowed": True,
        }



class TestSuiteForm(EnvConstrainedAddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=tcmforms.BareTextarea)
    product = tcmforms.ModelChoiceField(
        option_attrs=lambda p: {"data-product-id": p.id})
    cases = tcmforms.ModelMultipleChoiceField(
        required=False,
        label_from_instance=lambda c: c.name,
        option_attrs=product_id_attrs)


    no_edit_fields = ["product"]
    assign_later = ["cases"]
    entryclass = TestSuite
    listclass = TestSuiteList
    parent_name = "product"



class TestCaseForm(EnvConstrainedAddEditForm):
    name = forms.CharField()
    product = tcmforms.ModelChoiceField()
    # @@@ tags = forms.CharField(required=False)


    no_edit_fields = ["name", "product"]
    entryclass = TestCaseVersion
    listclass = TestCaseList
    extra_creation_data = {
        "maxAttachmentSizeInMbytes": 0,
        "maxNumberOfAttachments": 0,
        "description": "",
        }

    def create_formsets(self, *args, **kwargs):
        self.steps_formset = StepFormSet(
            *args, **dict(kwargs, prefix="steps"))

        super(TestCaseForm, self).create_formsets(*args, **kwargs)


    def is_valid(self):
        return (
            self.steps_formset.is_valid() and
            super(TestCaseForm, self).is_valid()
            )


    def save(self):
        self.steps_formset.save(self.instance)
        super(TestCaseForm, self).save()

        return self.instance

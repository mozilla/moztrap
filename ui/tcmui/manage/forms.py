import floppyforms as forms

from ..core import forms as tcmforms

from ..products.models import Product, ProductList
from ..testcases.forms import StepFormSet
from ..testcases.models import (
    TestSuite, TestSuiteList, TestCaseVersion, TestCaseList)
from ..testexecution.models import (
    TestCycle, TestCycleList, TestRun, TestRunList)



def product_id_attrs(obj):
    return {"data-product-id": obj.product.id}



class ProductForm(tcmforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=tcmforms.BareTextarea)
    team = tcmforms.ModelMultipleChoiceField(required=False)


    assign_later = ["team"]
    entryclass = Product
    listclass = ProductList


    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        if "instance" not in kwargs:
            self.base_fields["profile"] = tcmforms.ModelChoiceField()

        super(ProductForm, self).__init__(*args, **kwargs)


    @property
    def extra_creation_data(self):
        return {"company": self.company}



class TestCycleForm(tcmforms.AddEditForm):
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
    extra_creation_data = {
        "communityAccessAllowed": True,
        "communityAuthoringAllowed": True,
        }



class TestRunForm(tcmforms.AddEditForm):
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
    extra_creation_data = {
        "selfAssignLimit": 0,
        "selfAssignAllowed": True,
        }



class TestSuiteForm(tcmforms.AddEditForm):
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



class TestCaseForm(tcmforms.AddEditForm):
    name = forms.CharField()
    product = tcmforms.ModelChoiceField()
    # @@@ tags = forms.CharField(required=False)


    no_edit_fields = ["product"]
    entryclass = TestCaseVersion
    listclass = TestCaseList
    extra_creation_data = {
        "maxAttachmentSizeInMbytes": 0,
        "maxNumberOfAttachments": 0,
        "automationUri": "",
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


    def edit_clean(self):
        ret = super(TestCaseForm, self).edit_clean()

        # Name field can't be edited via TestCaseVersion, so we do it via the
        # TestCase proper
        tc = TestCaseList.get_by_id(self.instance.testCaseId, auth=self.auth)
        tc.name = self.instance.name = self.cleaned_data["name"]
        try:
            tc.put()
        except self.instance.Conflict, e:
            self.handle_error(self.instance, e)

        return ret



    def save(self):
        self.steps_formset.save(self.instance)

        return super(TestCaseForm, self).save()

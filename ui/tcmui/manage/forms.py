import floppyforms as forms

from ..core import forms as tcmforms
from ..environments.forms import EnvironmentConstraintFormSet
from ..environments.models import EnvironmentGroupList

from ..testexecution.models import TestCycle, TestCycleList



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


    def create_formsets(self, *args, **kwargs):
        if self.instance is None:
            possible_groups = EnvironmentGroupList.ours(auth=self.auth)
        else:
            possible_groups = self.instance.product.environmentgroups
        self.env_formset = EnvironmentConstraintFormSet(
            *args,
            **dict(kwargs, groups=possible_groups, prefix="environments")
        )


    def is_valid(self):
        return (
            self.env_formset.is_valid() and
            super(TestCycleForm, self).is_valid()
            )


    def save(self):
        self.env_formset.save(
            self.instance, self.instance.product.environmentgroups)

        return self.instance

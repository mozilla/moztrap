import floppyforms as forms

from ..core.forms import AddEditForm, BareTextarea, ModelChoiceField
from ..environments.forms import EnvironmentConstraintFormSet
from ..environments.models import EnvironmentGroupList

from ..testexecution.models import TestCycle, TestCycleList



class TestCycleForm(AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=BareTextarea)
    product = ModelChoiceField()
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)


    no_edit_fields = ["product"]
    model_choice_fields = {"product": "products"}
    field_mapping = {
        "start_date": "startDate",
        "end_date": "endDate"}
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

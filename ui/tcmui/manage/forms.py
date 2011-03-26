import floppyforms as forms

from ..core.forms import BareTextarea
from ..environments.forms import EnvironmentConstraintFormSet
from ..environments.models import EnvironmentGroupList

from ..testexecution.models import TestCycle, TestCycleList



class TestCycleForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=BareTextarea)
    product = forms.ChoiceField(choices=[])
    start_date = forms.DateField()
    end_date = forms.DateField()


    def __init__(self, *args, **kwargs):
        products = kwargs.pop("products", [])
        super(TestCycleForm, self).__init__(*args, **kwargs)

        self.products = {}
        choices = []
        for p in products:
            choices.append((p.id, p.name))
            self.products[p.id] = p
        self.fields["product"].choices = choices
        self.auth = products.auth

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
            self.env_formset.is_valid() and
            super(TestCycleForm, self).is_valid()
            )


    def clean(self):
        if all([k in self.cleaned_data for k in
                ["name", "description", "product", "start_date", "end_date"]]):
            cycle = TestCycle(
                name=self.cleaned_data["name"],
                description=self.cleaned_data["description"],
                product=self.products[self.cleaned_data["product"]],
                startDate=self.cleaned_data["start_date"],
                endDate=self.cleaned_data["end_date"],
                )
            try:
                TestCycleList.get(auth=self.auth).post(cycle)
            except TestCycleList.Conflict, e:
                if e.response_error == "duplicate.name":
                    self._errors["name"] = self.error_class(
                        ["This name is already in use."])
                else:
                    raise forms.ValidationError(
                        'Unknown conflict "%s"; please correct and try again.'
                        % e.response_error)
            else:
                self.cycle = cycle
        return self.cleaned_data


    def save(self):
        self.env_formset.save(self.cycle, self.cycle.product.environmentgroups)

        return self.cycle

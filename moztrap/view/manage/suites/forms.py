"""
Management forms for suites.

"""
import floppyforms as forms

from moztrap import model
from moztrap.view.lists import filters
from moztrap.view.utils import mtforms



class SuiteForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for adding/editing suites."""
    cases = mtforms.MTModelMultipleChoiceField(
        queryset=model.Case.objects.all(),
        required=False,
        choice_attrs=mtforms.product_id_attrs,
        widget=mtforms.FilteredSelectMultiple(
            choice_template="manage/suite/case_select/_case_select_item.html",
            listordering_template=(
                "manage/suite/case_select/_case_select_listordering.html"),
            filters=[
                filters.ChoicesFilter(
                    "status", choices=model.CaseVersion.STATUS),
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "tag", lookup="tags", queryset=model.Tag.objects.all()),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
        )
    product = mtforms.MTModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})

    class Meta:
        model = model.Suite
        fields = ["product", "name", "description", "status"]
        widgets = {
            "name": forms.TextInput,
            "description": mtforms.BareTextarea,
            "status": forms.Select,
            }


    def save(self, user=None):
        """Save the suite and case associations."""
        user = user or self.user
        suite = super(SuiteForm, self).save(user=user)

        suite.suitecases.all().delete(permanent=True)
        for i, case in enumerate(self.cleaned_data["cases"]):
            model.SuiteCase.objects.create(
                suite=suite, case=case, order=i, user=user)

        return suite



class AddSuiteForm(SuiteForm):
    """Form for adding a suite."""
    pass



class EditSuiteForm(SuiteForm):
    """Form for editing a suite."""
    def __init__(self, *args, **kwargs):
        """Initialize EditSuiteForm; no changing product."""
        super(EditSuiteForm, self).__init__(*args, **kwargs)

        # for suites with cases in them, product is readonly and case options
        # are filtered to that product
        if self.instance.cases.exists():
            pf = self.fields["product"]
            pf.queryset = pf.queryset.filter(pk=self.instance.product_id)
            pf.readonly = True

            cf = self.fields["cases"]
            cf.queryset = cf.queryset.filter(product=self.instance.product_id)

        self.initial["cases"] = list(
            self.instance.cases.values_list("id", flat=True))

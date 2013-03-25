"""
Management forms for suites.

"""
from django.core.exceptions import ValidationError
import floppyforms as forms

from moztrap import model
from moztrap.view.lists import filters
from moztrap.view.utils import mtforms



class SuiteForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for adding/editing suites."""
    cases = mtforms.MTMultipleChoiceField(
        required=False,
        widget=mtforms.FilteredSelectMultiple(
            choice_template="manage/multi_select/case_select/_case_select_item.html",
            listordering_template=(
                "manage/multi_select/case_select/_case_select_listordering.html"),
            filters=[
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


    def clean_cases(self):
        """
        Make sure all the ids for the cases are valid and populate
        self.cleaned_data with the real objects.
        """
        # fetch the case objects in one query, but loses order.
        cases = dict((unicode(x.id), x) for x in
            model.Case.objects.filter(pk__in=self.cleaned_data["cases"]))

        # put them back in order and remove dups, if any
        try:
            # remove dups, if there are any.
            clean_cases = []
            for case_id in self.cleaned_data["cases"]:
                case = cases[case_id]
                if case not in clean_cases:
                    clean_cases.append(case)

            # if number is different, then add this to changed data
            if (("cases" in self.initial and self.initial["cases"] != self.cleaned_data["cases"]) or
                len(self.cleaned_data["cases"]) is not len(clean_cases)):
                    self.changed_data.append("cases")

            return clean_cases
        except KeyError as e:
            raise ValidationError("Not a valid case for this suite.")


    def save(self, user=None):
        """Save the suite and case associations."""
        user = user or self.user
        suite = super(SuiteForm, self).save(user=user)

        if "cases" in self.changed_data:
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

        self.initial["cases"] = list(
            self.instance.cases.values_list(
                "id",
                flat=True,
                ).order_by("suitecases__order"))

        # for suites with cases in them, product is readonly and case options
        # are filtered to that product
        if self.instance.cases.exists():
            pf = self.fields["product"]
            pf.queryset = pf.queryset.filter(pk=self.instance.product_id)
            pf.readonly = True

            # ajax populates available and included cases on page load

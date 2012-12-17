"""
Management forms for tags.

"""
from django.core.exceptions import ValidationError
import floppyforms as forms

from .... import model

from ...utils import mtforms
from ...lists import filters




class TagForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for tags."""

    cases = mtforms.MTMultipleChoiceField(
        required=False,
        widget=mtforms.FilteredSelectMultiple(
            choice_template="manage/multi_select/case_select/_case_select_item.html",
            listordering_template=(
                "manage/multi_select/case_select/_case_select_listordering.html"),
            filters=[
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "product version", lookup="productversion",
                    queryset=model.ProductVersion.objects.all()),
                filters.ModelFilter(
                    "tag", lookup="tags", queryset=model.Tag.objects.all()),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
    )

    class Meta:
        model = model.Tag
        fields = ["name", "description", "product"]
        widgets = {
            "name": forms.TextInput,
            "description": mtforms.BareTextarea,
            "product": forms.Select,
            }


    def clean_cases(self):
        """
        Make sure all the ids for the cases are valid and populate
        self.cleaned_data with the real objects.
        """
        cases = dict((unicode(x.id), x) for x in
            model.Case.objects.filter(pk__in=self.cleaned_data["cases"]))
        try:
            return [cases[x] for x in self.cleaned_data["cases"]]
        except KeyError as e:
            raise ValidationError("Not a valid case for this suite.")


    def save(self, user=None):
        """Save the suite and case associations."""
        user = user or self.user
        suite = super(TagForm, self).save(user=user)

        suite.suitecases.all().delete(permanent=True)
        for i, case in enumerate(self.cleaned_data["cases"]):
            model.SuiteCase.objects.create(
                suite=suite, case=case, order=i, user=user)

        return suite



class EditTagForm(TagForm):
    """Form for editing a tag."""
    def __init__(self, *args, **kwargs):
        """Initialize form; restrict tag product choices."""
        super(EditTagForm, self).__init__(*args, **kwargs)

        products_tagged = model.Product.objects.filter(
            cases__versions__tags=self.instance).distinct()
        count = products_tagged.count()

        pf = self.fields["product"]

        if count > 1:
            pf.queryset = model.Product.objects.none()
        elif count == 1:
            pf.queryset = products_tagged



class AddTagForm(TagForm):
    """Form for adding a tag."""
    pass

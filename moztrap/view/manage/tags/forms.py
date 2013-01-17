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

    caseversions = mtforms.MTMultipleChoiceField(
        required=False,
        widget=mtforms.FilteredSelectMultiple(
            listordering_template=(
                "manage/tag/caseversion_select/_caseversion_select_listordering.html"),
            filters=[
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "product version",
                    key="productversion",
                    lookup="productversion",
                    queryset=model.ProductVersion.objects.all(),
                    ),
                filters.ModelFilter(
                    "tag", lookup="tags", queryset=model.Tag.objects.all()),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
    )
    product = mtforms.MTModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id},
        required=False)

    class Meta:
        model = model.Tag
        fields = ["name", "product", "description"]
        widgets = {
            "name": forms.TextInput,
            "product": forms.Select,
            "description": mtforms.BareTextarea,
            }


    def clean_caseversions(self):
        """
        Make sure all the ids for the cases are valid and populate
        self.cleaned_data with the real objects.
        """
        caseversions = dict((unicode(x.id), x) for x in
            model.CaseVersion.objects.filter(
                pk__in=self.cleaned_data["caseversions"]))
        try:
            return [caseversions[x] for x in self.cleaned_data["caseversions"]]
        except KeyError as e:
            raise ValidationError("Not a valid caseversion for this tag.")


    def save(self, user=None):
        """Save the tag and case associations."""
        user = user or self.user
        tag = super(TagForm, self).save(user=user)

        # it's possible the user submitted the form before the ajax loaded
        # the included and available cases.  So ``caseversions`` would not
        # show in the changed_data.  If that's the case, we prevent updating
        # the list of cases.
        if "caseversions" in self.changed_data:
            TagCV = tag.caseversions.through

            # @@@ used to be delete() instead of clear.  May be remove?
            # why is delete() ok for cases of suites?  must be some special checking
            # for that.
            tag.caseversions.clear()
            tcv_list = [TagCV(tag=tag, caseversion=cv)
                for cv in self.cleaned_data["caseversions"]]

            TagCV.objects.bulk_create(tcv_list)

        return tag



class EditTagForm(TagForm):
    """Form for editing a tag."""
    def __init__(self, *args, **kwargs):
        """Initialize form; restrict tag product choices."""
        super(EditTagForm, self).__init__(*args, **kwargs)

        # get all the cases this tag is applied to, if the cases belong to
        # a single product, this tag can be set to global or to that product.
        # if it's applied to cases from multiple products, then it must
        # remain global.
        products_tagged = model.Product.objects.filter(
            cases__versions__tags=self.instance).distinct()
        count = products_tagged.count()

        pf = self.fields["product"]

        if count > 1:
            # ro - no options
            # - no product set, cases applied from multiple products
            pf.queryset = model.Product.objects.none()
            pf.readonly = True
        elif count == 1:
            # rw - that product or none
            # - no product set, cases applied from single product
            # - product set, cases applied
            pf.queryset = products_tagged

        # else:
        # rw - all product options
        # - no product set, no cases applied
        # - product set, no cases applied


class AddTagForm(TagForm):
    """Form for adding a tag."""
    pass

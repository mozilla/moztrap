"""
Management forms for product versions.

"""
import floppyforms as forms

from .... import model

from ...utils import mtforms




class BaseProductVersionForm(mtforms.NonFieldErrorsClassFormMixin,
                             mtforms.MTModelForm):
    """Base Form for productversions."""

    class Meta:
        model = model.ProductVersion
        fields = ["version", "codename"]
        widgets = {
            "version": forms.TextInput,
            "codename": forms.TextInput,
            }



class EditProductVersionForm(BaseProductVersionForm):
    """Form for editing productversions."""

    fill_from = mtforms.MTModelChoiceField(  # pragma: no cover
        required=False,
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=mtforms.product_id_attrs,
        label_from_instance=lambda pv: pv.version,
        )


    class Meta:
        model = model.ProductVersion
        fields = ["version", "codename"]
        widgets = {
            "version": forms.TextInput,
            "codename": forms.TextInput,
            }


    def __init__(self, *args, **kwargs):
        super(EditProductVersionForm, self).__init__(*args, **kwargs)
        self.fields["fill_from"].queryset = self.instance.product.versions.exclude(
            pk=self.instance.pk)


    def save(self, user=None):
        """Save and return product version; copy envs."""
        pv = super(EditProductVersionForm, self).save(user=user)

        fill_from = self.cleaned_data.get("fill_from")
        if fill_from:
            # get the cases we already have in this version
            existing = pv.caseversions.all().values_list("case_id", flat=True)
            for cv in fill_from.caseversions.exclude(case_id__in=existing):
                cv.clone(overrides={"productversion": pv, "name": cv.name})

        return pv



class AddProductVersionForm(BaseProductVersionForm):
    """Form for adding a productversion."""
    product = mtforms.MTModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})
    clone_from = mtforms.MTModelChoiceField(  # pragma: no cover
        required=False,
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=mtforms.product_id_attrs,
        label_from_instance=lambda pv: pv.version,
        )


    class Meta(EditProductVersionForm.Meta):
        fields = ["product", "version", "codename"]
        widgets = EditProductVersionForm.Meta.widgets.copy()


    def save(self, user=None):
        """Save and return product version; copy envs."""
        pv = super(AddProductVersionForm, self).save(user=user)

        clone_from = self.cleaned_data.get("clone_from")
        if clone_from:
            pv.environments.add(*clone_from.environments.all())
            for cv in clone_from.caseversions.all():
                cv.clone(overrides={"productversion": pv, "name": cv.name})

        return pv

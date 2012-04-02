"""
Management forms for product versions.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class EditProductVersionForm(ccforms.NonFieldErrorsClassFormMixin,
                             ccforms.CCModelForm):
    """Form for editing productversions."""
    class Meta:
        model = model.ProductVersion
        fields = ["version", "codename"]
        widgets = {
            "version": forms.TextInput,
            "codename": forms.TextInput,
            }



class AddProductVersionForm(EditProductVersionForm):
    """Form for adding a productversion."""
    product = ccforms.CCModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})
    clone_from = ccforms.CCModelChoiceField(  # pragma: no cover
        required=False,
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=ccforms.product_id_attrs,
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

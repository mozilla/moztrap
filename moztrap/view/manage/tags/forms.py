"""
Management forms for tags.

"""
import floppyforms as forms

from .... import model

from ...utils import mtforms




class TagForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for tags."""
    class Meta:
        model = model.Tag
        fields = ["name", "product"]
        widgets = {
            "name": forms.TextInput,
            "product": forms.Select,
            }



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

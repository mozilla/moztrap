"""
Management forms for tags.

"""

from django.core.urlresolvers import reverse

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

        # TODO: genericize for runs and cases
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



class ApplyTagsFormMixin(object):
    """
    Base form for all forms that handle tags.

    Provides tags fields.

    """

    def __init__(self, *args, **kwargs):
        """Initialize form; pull out user from kwargs, set up data-allow-new."""
        self.user = kwargs.pop("user", None)

        super(ApplyTagsFormMixin, self).__init__(*args, **kwargs)

        self.fields["add_tags"] = forms.CharField(
            widget=mtforms.AutocompleteInput(
                url=lambda: reverse("manage_tags_autocomplete")),
            required=False)
        self.fields["add_tags"].widget.attrs["data-allow-new"] = (
            "true"
            if (self.user and self.user.has_perm("tags.manage_tags"))
            else "false"
            )


    def clean(self):
        """Can't create new tags without appropriate permissions."""
        if (self.data.get("tag-newtag") and
            not (self.user and self.user.has_perm("tags.manage_tags"))):
            raise forms.ValidationError(
                "You do not have permission to create new tags.")
        return self.cleaned_data


    def save_new_tags(self, product=None):
        """Save new tags and add them to the list of tags to assign."""
        tags = self.cleaned_data.setdefault("tags", set())
        tags.update([int(tid) for tid in self.data.getlist("tag-tag")])

        new_tags = self.data.getlist("tag-newtag")

        for name in new_tags:
            # @@@ should pass in user here, need MTQuerySet.get_or_create
            t, created = model.Tag.objects.get_or_create(
                name=name, product=product)
            tags.add(t.id)


    def save_tags(self, tagged_object):
        """
        Update set of tags assigned to ``tagged_object``.

        ``tagged_object`` must have a many to many relationship with the
        Tag model.

        """
        tags = self.cleaned_data.get("tags", set())

        current_tags = set([t.id for t in tagged_object.tags.all()])

        tagged_object.tags.add(*tags.difference(current_tags))
        tagged_object.tags.remove(*current_tags.difference(tags))

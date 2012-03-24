"""
Manage forms for environments.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class ProfileForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for profiles."""
    class Meta:
        model = model.Profile
        fields = ["name"]
        widgets = {
            "name": forms.TextInput,
            }



class EditProfileForm(ProfileForm):
    """Form for editing a profile."""
    # @@@ unused currently
    pass



class EnvironmentElementSelectMultiple(ccforms.CCSelectMultiple):
    """A widget for selecting multiple environment elements."""
    template_name = "manage/environment/element_select/_element_select.html"


    def get_context(self, *args, **kwargs):
        """Add category list, with elements for each category, to context."""
        ctx = super(EnvironmentElementSelectMultiple, self).get_context(
            *args, **kwargs)
        # maps category to list of available elements
        available = {}
        for c in ctx["choices"]:
            element = c[1].obj
            available.setdefault(element.category, []).append(element)
        # ensure we also include empty categories
        categories = list(model.Category.objects.order_by("name"))
        for category in categories:
            # annotate with elements available in this widget
            category.choice_elements = available.get(category, [])
        ctx["categories"] = categories
        ctx["selected_element_ids"] = set(map(int, ctx["value"]))
        return ctx



class AddProfileForm(ProfileForm):
    """Form for adding a profile."""
    elements = ccforms.CCModelMultipleChoiceField(
        queryset=model.Element.objects.order_by(
            "category", "name").select_related(),
        widget=EnvironmentElementSelectMultiple,
        error_messages={"required": "Please select at least one element."})


    def save(self, user=None):
        """Create and return the new profile."""
        return model.Profile.generate(
            self.cleaned_data["name"],
            *self.cleaned_data["elements"],
            **{"user": user or self.user}
            )

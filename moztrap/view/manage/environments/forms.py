"""
Manage forms for environments.

"""
import floppyforms as forms

from .... import model

from ...utils import mtforms




class ProfileForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
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



class EnvironmentElementSelectMultiple(mtforms.MTSelectMultiple):
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
    elements = mtforms.MTModelMultipleChoiceField(
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



class PopulateProductVersionEnvsForm(mtforms.NonFieldErrorsClassFormMixin,
                                     forms.Form,
                                     ):
    """Form for populating the envs of a productversion."""
    source = forms.ChoiceField(
        label="Populate with environments from", choices=[])


    def __init__(self, *args, **kwargs):
        """Initialize form; takes productversion kwarg, sets source choices."""
        self.productversion = kwargs.pop("productversion")

        super(PopulateProductVersionEnvsForm, self).__init__(*args, **kwargs)

        choices = []
        self.choice_map = {}
        for pv in self.productversion.product.versions.exclude(
                pk=self.productversion.pk):
            key = "productversion-{0}".format(pv.pk)
            choices.append((key, unicode(pv)))
            self.choice_map[key] = pv

        for profile in model.Profile.objects.all():
            key = "profile-{0}".format(profile.pk)
            choices.append((key, unicode(profile)))
            self.choice_map[key] = profile

        self.fields["source"].choices = choices


    def save(self):
        """Save envs from selected source to productversion."""
        source = self.choice_map[self.cleaned_data["source"]]

        self.productversion.add_envs(*source.environments.all())

        return self.productversion

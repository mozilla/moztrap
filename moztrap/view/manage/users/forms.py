"""
Management forms for users.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class UserForm(ccforms.NonFieldErrorsClassFormMixin, forms.ModelForm):
    """Base form for users."""
    class Meta:
        model = model.User
        fields = ["username", "email", "is_active", "groups"]
        widgets = {
            "username": forms.TextInput,
            "email": forms.TextInput,
            "is_active": forms.CheckboxInput,
            "groups": forms.SelectMultiple,
            }


    def __init__(self, *args, **kwargs):
        """Initialize user form; labels "groups" field as "roles"."""
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields["groups"].label = "roles"



class EditUserForm(UserForm):
    """Form for editing a user."""
    pass



class AddUserForm(UserForm):
    """Form for adding a user."""
    pass

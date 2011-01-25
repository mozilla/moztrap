import floppyforms as forms

from ..core.api import admin
from ..core.forms import RemoteObjectForm

from .models import User, UserList
from .util import get_user



class UserPlaceholdersMixin(object):
    def __init__(self, *args, **kwargs):
        super(UserPlaceholdersMixin, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            if fieldname == "email":
                placeholder = "email address"
            else:
                placeholder = field.label
            field.widget.attrs.setdefault("placeholder", placeholder)



class LoginForm(UserPlaceholdersMixin, RemoteObjectForm):
    email = forms.EmailField(label="email")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="password")


    def clean(self):
        if "email" in self.cleaned_data and "password" in self.cleaned_data:
            self.user = get_user(
                self.cleaned_data["email"],
                self.cleaned_data["password"]
                )
            if self.user is None:
                raise forms.ValidationError(
                    "Sorry, that email/password combination doesn't match "
                    "any users in our records.")
        return self.cleaned_data



class RegistrationForm(UserPlaceholdersMixin, RemoteObjectForm):
    firstName = forms.CharField(label="first name")
    lastName = forms.CharField(label="last name")
    screenName = forms.CharField(label="username")
    email = forms.EmailField(label="email")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="password")
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="confirm password")


    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super(RegistrationForm, self).__init__(*args, **kwargs)


    def clean(self):
        if "password" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password2"]:
                raise forms.ValidationError("Provided passwords do not match.")
            del self.cleaned_data["password2"]

        if all(k in self.cleaned_data
               for k in ["firstName", "lastName", "screenName",
                         "email", "password"]):
            data = self.cleaned_data
            data["company"] = self.company
            user = User(**data)
            UserList.get(auth=admin).post(user)
            self.user = user
        return self.cleaned_data

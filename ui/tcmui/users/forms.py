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


    def clean_password2(self):
        password1 = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("Provided passwords didn't match.")
        return password2


    def clean(self):
        if all(k in self.cleaned_data
               for k in ["firstName", "lastName", "screenName",
                         "email", "password", "password2"]):
            data = self.cleaned_data
            del data["password2"]
            data["company"] = self.company
            user = User(**data)
            try:
                UserList.get(auth=admin).post(user)
            except UserList.Conflict, e:
                if "Screen name" in e.response_error:
                    self._errors["screenName"] = self.error_class(
                        ["This username is already in use."])
                elif "Email" in e.response_error:
                    self._errors["email"] = self.error_class(
                        ["This email address is already in use."])
                else:
                    raise forms.ValidationError(
                        "Unknown conflict; please try again.")
            else:
                self.user = user
        return self.cleaned_data

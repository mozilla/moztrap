import floppyforms as forms

from ..core.api import admin
from ..core.forms import RemoteObjectForm
from ..static import userstatus

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
                    "That email/password combination doesn't match "
                    "any users in our records.")
            if self.user.userStatus.id == userstatus.INACTIVE:
                raise forms.ValidationError(
                    "This user has not been activated. Please check your email "
                    "for an activation link.")
            elif self.user.userStatus.id == userstatus.DISABLED:
                raise forms.ValidationError(
                    "This user account has been disabled.")
            elif self.user.userStatus.id != userstatus.ACTIVE:
                raise forms.ValidationError(
                    "This user account is not active.")
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
                if e.response_error == "screenname.in.use":
                    self._errors["screenName"] = self.error_class(
                        ["This username is already in use."])
                elif e.response_error == "email.in.use":
                    self._errors["email"] = self.error_class(
                        ["This email address is already in use."])
                else:
                    raise forms.ValidationError(
                        'Unknown conflict "%s"; please correct and try again.'
                        % e.response_error)
            else:
                self.user = user
        return self.cleaned_data

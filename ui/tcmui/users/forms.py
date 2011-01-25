import floppyforms as forms

from ..core.forms import RemoteObjectForm



class RegistrationForm(RemoteObjectForm):
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
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            if fieldname == "email":
                placeholder = "email address"
            else:
                placeholder = field.label
            field.widget.attrs.setdefault("placeholder", placeholder)


    def clean(self):
        if "password" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password2"]:
                raise forms.ValidationError("Provided passwords do not match.")
            del self.cleaned_data["password2"]
        return self.cleaned_data

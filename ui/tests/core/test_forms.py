from mock import patch
from unittest2 import TestCase



class TestNonFieldErrorsClassFormMixin(TestCase):
    @property
    def mixin(self):
        from tcmui.core.forms import NonFieldErrorsClassFormMixin
        return NonFieldErrorsClassFormMixin


    @property
    def form_class(self):
        from django import forms

        class PersonForm(self.mixin, forms.Form):
            name = forms.CharField()
            age = forms.IntegerField()

            def clean(self):
                if (self.cleaned_data.get("name") == "Shakespeare" and
                    self.cleaned_data.get("age", 0) < 400):
                    raise forms.ValidationError("Too young to be Shakespeare.")

        return PersonForm


    def test_non_field_errorlist(self):
        form = self.form_class({"name": "Shakespeare", "age": "25"})

        nfe = form.non_field_errors()

        self.assertTrue('class="errorlist nonfield"' in unicode(nfe))


    def test_field_errorlist(self):
        form = self.form_class({"name": "Joe"})

        fe = unicode(form["age"].errors)

        self.assertTrue('class="' in fe)
        self.assertFalse("nonfield" in fe)



class RemoteObjectFormTest(TestCase):
    @property
    def form_class(self):
        import floppyforms as forms
        from tcmui.core.forms import RemoteObjectForm

        class PersonForm(RemoteObjectForm):
            name = forms.CharField()
            birthday = forms.DateField()

        return PersonForm


    def test_datefield_placeholder(self):
        self.assertEqual(
            self.form_class().fields["birthday"].widget.attrs["placeholder"],
            "mm/dd/yyyy")



class AddEditFormTest(TestCase):
    @property
    def form_class(self):
        from tcmui.core.forms import AddEditForm
        return AddEditForm


    @patch("tcmui.core.forms.errors.error_message_and_fields")
    def test_non_field_errors_dont_pass_silently(self, emaf):
        emaf.return_value = ("unknown error", [])
        obj, err = ("fake obj", "fake err")

        f = self.form_class(auth="auth")

        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            f.handle_error(obj, err)

        emaf.assert_called_once_with(obj, err)

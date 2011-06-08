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

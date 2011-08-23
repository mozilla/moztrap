from mock import patch, Mock
from unittest2 import TestCase



class TestNonFieldErrorsClassFormMixin(TestCase):
    @property
    def mixin(self):
        from ccui.core.forms import NonFieldErrorsClassFormMixin
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


    def test_no_nonfield_errors(self):
        form = self.form_class({"name": "Joe", "age": "25"})

        self.assertEqual(unicode(form.non_field_errors()), u"")



class RemoteObjectFormTest(TestCase):
    @property
    def form_class(self):
        import floppyforms as forms
        from ccui.core.forms import RemoteObjectForm

        class PersonForm(RemoteObjectForm):
            name = forms.CharField()
            birthday = forms.DateField()

        return PersonForm


    def test_datefield_placeholder(self):
        self.assertEqual(
            self.form_class().fields["birthday"].widget.attrs["placeholder"],
            "yyyy-mm-dd")



class AddEditFormTest(TestCase):
    @property
    def form_class(self):
        from ccui.core.forms import AddEditForm
        return AddEditForm


    @patch("ccui.core.forms.errors.error_message_and_fields")
    def test_non_field_errors_dont_pass_silently(self, emaf):
        emaf.return_value = ("unknown error", [])
        obj, err = ("fake obj", "fake err")

        f = self.form_class(auth="auth")

        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            f.handle_error(obj, err)

        emaf.assert_called_once_with(obj, err)


    def test_no_edit_fields(self):
        import floppyforms as forms

        class PersonForm(self.form_class):
            name = forms.CharField()
            age = forms.CharField()

            no_edit_fields = ["age"]

        f = PersonForm(instance=Mock(), auth=Mock())

        self.assertEqual(f.fields["age"].read_only, True)



class BareTextareaTest(TestCase):
    def test_no_attrs(self):
        from ccui.core.forms import BareTextarea
        self.assertEqual(BareTextarea().attrs, {})



class ReadOnlyWidgetTest(TestCase):
    @property
    def widget(self):
        from ccui.core.forms import ReadOnlyWidget
        return ReadOnlyWidget


    def test_simple(self):
        self.assertEqual(
            self.widget().render("name", "value"),
            u'value<input type="hidden" name="name" value="value">\n'
            )


    def test_attrs(self):
        self.assertEqual(
            self.widget().render("name", "value", {"attr": "val"}),
            u'value<input type="hidden" name="name" value="value" attr="val">\n'
            )


    def test_choices(self):
        widget = self.widget()
        widget.choices = [(1, "one"), (2, "two")]
        self.assertEqual(
            widget.render("name", 1),
            u'one<input type="hidden" name="name" value="1">\n'
            )


    def test_choices_bad_choice(self):
        widget = self.widget()
        widget.choices = [(1, "one"), (2, "two")]
        self.assertEqual(
            widget.render("name", 3),
            u'3<input type="hidden" name="name" value="3">\n'
            )


    def test_choices_iterator(self):
        widget = self.widget()
        widget.choices = (i for i in [(1, "one"), (2, "two")])
        self.assertEqual(
            widget.render("name", 2),
            u'two<input type="hidden" name="name" value="2">\n'
            )


    def test_choices_extra_data(self):
        widget = self.widget()
        widget.choices = [(1, "one", "extra"), (2, "two", "extra")]
        self.assertEqual(
            widget.render("name", 1),
            u'one<input type="hidden" name="name" value="1">\n'
            )

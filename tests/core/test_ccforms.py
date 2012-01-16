# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for Case Conductor form utilities.

"""
from django.utils.unittest import TestCase

from django import forms

from cc.core import ccforms



class PersonForm(ccforms.NonFieldErrorsClassFormMixin, forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()

    def clean(self):
        if (self.cleaned_data.get("name") == "Shakespeare" and
            self.cleaned_data.get("age", 0) < 400):
            raise forms.ValidationError("Too young to be Shakespeare.")



class TestNonFieldErrorsClassFormMixin(TestCase):
    def test_non_field_errorlist(self):
        form = PersonForm({"name": "Shakespeare", "age": "25"})

        nfe = form.non_field_errors()

        self.assertTrue('class="errorlist nonfield"' in unicode(nfe))


    def test_field_errorlist(self):
        form = PersonForm({"name": "Joe"})

        fe = unicode(form["age"].errors)

        self.assertTrue('class="' in fe)
        self.assertFalse("nonfield" in fe)


    def test_no_nonfield_errors(self):
        form = PersonForm({"name": "Joe", "age": "25"})

        self.assertEqual(unicode(form.non_field_errors()), u"")



class BareTextareaTest(TestCase):
    def test_no_attrs(self):
        self.assertEqual(ccforms.BareTextarea().attrs, {})



class ReadOnlyWidgetTest(TestCase):
    def test_simple(self):
        self.assertEqual(
            ccforms.ReadOnlyWidget().render("name", "value"),
            u'value<input type="hidden" name="name" value="value">\n'
            )


    def test_attrs(self):
        self.assertEqual(
            ccforms.ReadOnlyWidget().render("name", "value", {"attr": "val"}),
            u'value<input type="hidden" name="name" value="value" attr="val">\n'
            )


    def test_choices(self):
        widget = ccforms.ReadOnlyWidget()
        widget.choices = [(1, "one"), (2, "two")]
        self.assertEqual(
            widget.render("name", 1),
            u'one<input type="hidden" name="name" value="1">\n'
            )


    def test_choices_bad_choice(self):
        widget = ccforms.ReadOnlyWidget()
        widget.choices = [(1, "one"), (2, "two")]
        self.assertEqual(
            widget.render("name", 3),
            u'3<input type="hidden" name="name" value="3">\n'
            )


    def test_choices_iterator(self):
        widget = ccforms.ReadOnlyWidget()
        widget.choices = (i for i in [(1, "one"), (2, "two")])
        self.assertEqual(
            widget.render("name", 2),
            u'two<input type="hidden" name="name" value="2">\n'
            )


    def test_choices_extra_data(self):
        widget = ccforms.ReadOnlyWidget()
        widget.choices = [(1, "one", "extra"), (2, "two", "extra")]
        self.assertEqual(
            widget.render("name", 1),
            u'one<input type="hidden" name="name" value="1">\n'
            )

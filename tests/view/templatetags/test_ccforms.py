# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Tests for Case Conductor form-rendering template tags and filters.

"""
from django.utils.unittest import TestCase

from mock import patch
import floppyforms as forms

from cc.view.templatetags import ccforms



class PersonForm(forms.Form):
    name = forms.CharField(initial="none", required=True)
    level = forms.ChoiceField(
        choices=(("b", "Beginner"), ("a", "Advanced")), required=False)
    awesome = forms.BooleanField(required=False)



class FieldFilterTests(TestCase):
    """Tests for form field filters."""
    def test_placeholder(self):
        """``placeholder`` filter sets placeholder attribute."""
        bf = ccforms.placeholder(PersonForm()["name"], "Placeholder")
        self.assertIn('placeholder="Placeholder"', unicode(bf))


    @patch("cc.view.templatetags.ccforms.render_to_string")
    def test_label(self, render_to_string):
        """``label`` filter renders field label from template."""
        render_to_string.return_value = "<label>something</label>"
        bf = PersonForm()["name"]

        label = ccforms.label(bf)

        self.assertEqual(label, "<label>something</label>")
        render_to_string.assert_called_with(
            "forms/_label.html",
            {
                "label_text": "Name",
                "id": "id_name",
                "field": bf
                }
            )


    @patch("cc.view.templatetags.ccforms.render_to_string")
    def test_label_override(self, render_to_string):
        """label filter allows overriding the label text."""
        bf = PersonForm()["name"]

        ccforms.label(bf, "override")

        render_to_string.assert_called_with(
            "forms/_label.html",
            {
                "label_text": "override",
                "id": "id_name",
                "field": bf
                }
            )

    def test_label_text(self):
        """``label_text`` filter returns field's default label text."""
        self.assertEqual(ccforms.label_text(PersonForm()["name"]), "Name")


    def test_value_text(self):
        """``value_text`` filter returns value of field."""
        self.assertEqual(
            ccforms.value_text(PersonForm({"name": "boo"})["name"]), "boo")


    def test_value_text_unbound(self):
        """``value_text`` filter returns default value of unbound field."""
        self.assertEqual(ccforms.value_text(PersonForm()["name"]), "none")


    def test_value_text_choices(self):
        """``value_text`` filter returns human-readable value of choicefield."""
        self.assertEqual(
            ccforms.value_text(PersonForm({"level": "a"})["level"]), "Advanced")


    def test_classes(self):
        """``classes`` filter sets widget's class attr if not set."""
        bf = PersonForm()["name"]

        bf = ccforms.classes(bf, "yo ma")

        self.assertIn('class="yo ma"', unicode(bf))


    def test_classes_append(self):
        """``classes`` filter appends to widget's class attr if set."""
        bf = PersonForm()["name"]
        bf.field.widget.attrs["class"] = "foo"

        bf = ccforms.classes(bf, "yo ma")

        self.assertIn('class="foo yo ma"', unicode(bf))


    def test_optional_false(self):
        """A required field should not be marked optional."""
        self.assertFalse(ccforms.optional(PersonForm()["name"]))


    def test_optional_true(self):
        """A non-required field should be marked optional."""
        self.assertTrue(ccforms.optional(PersonForm()["level"]))


    def test_optional_boolean(self):
        """A non-"required" BooleanField should not be marked optional."""
        self.assertFalse(ccforms.optional(PersonForm()["awesome"]))


    def test_attr(self):
        """``attr`` filter sets an attribute."""
        self.assertIn(
            'foo="bar"',
            unicode(ccforms.attr(PersonForm()["name"], "foo:bar")))


    def test_attr_no_value(self):
        """``attr`` filter sets a no-value attribute."""
        self.assertIn(
            "foo ", unicode(ccforms.attr(PersonForm()["name"], "foo")))


    def test_detect_checkbox(self):
        """``is_checkbox`` detects checkboxes."""
        f = PersonForm()

        self.assertTrue(ccforms.is_checkbox(f["awesome"]))


    def test_detect_(self):
        """``is_checkbox`` detects checkboxes."""
        f = PersonForm()

        self.assertFalse(ccforms.is_checkbox(f["level"]))

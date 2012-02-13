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
from mock import patch
import floppyforms as forms

from tests import case



class FieldFilterTests(case.TestCase):
    """Tests for form field filters."""
    @property
    def ccforms(self):
        """The module under test."""
        from cc.view.templatetags import ccforms
        return ccforms


    @property
    def form(self):
        """A sample form."""
        class PersonForm(forms.Form):
            name = forms.CharField(initial="none", required=True)
            level = forms.ChoiceField(
                choices=(("b", "Beginner"), ("a", "Advanced")), required=False)
            awesome = forms.BooleanField(required=False)

        return PersonForm



    def test_placeholder(self):
        """``placeholder`` filter sets placeholder attribute."""
        bf = self.ccforms.placeholder(self.form()["name"], "Placeholder")
        self.assertIn('placeholder="Placeholder"', unicode(bf))


    @patch("cc.view.templatetags.ccforms.render_to_string")
    def test_label(self, render_to_string):
        """``label`` filter renders field label from template."""
        render_to_string.return_value = "<label>something</label>"
        bf = self.form()["name"]

        label = self.ccforms.label(bf)

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
        bf = self.form()["name"]

        self.ccforms.label(bf, "override")

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
        self.assertEqual(self.ccforms.label_text(self.form()["name"]), "Name")


    def test_value_text(self):
        """``value_text`` filter returns value of field."""
        self.assertEqual(
            self.ccforms.value_text(self.form({"name": "boo"})["name"]), "boo")


    def test_value_text_unbound(self):
        """``value_text`` filter returns default value of unbound field."""
        self.assertEqual(self.ccforms.value_text(self.form()["name"]), "none")


    def test_value_text_choices(self):
        """``value_text`` filter returns human-readable value of choicefield."""
        self.assertEqual(
            self.ccforms.value_text(
                self.form({"level": "a"})["level"]), "Advanced")


    def test_classes(self):
        """``classes`` filter sets widget's class attr if not set."""
        bf = self.form()["name"]

        bf = self.ccforms.classes(bf, "yo ma")

        self.assertIn('class="yo ma"', unicode(bf))


    def test_classes_append(self):
        """``classes`` filter appends to widget's class attr if set."""
        bf = self.form()["name"]
        bf.field.widget.attrs["class"] = "foo"

        bf = self.ccforms.classes(bf, "yo ma")

        self.assertIn('class="foo yo ma"', unicode(bf))


    def test_optional_false(self):
        """A required field should not be marked optional."""
        self.assertFalse(self.ccforms.optional(self.form()["name"]))


    def test_optional_true(self):
        """A non-required field should be marked optional."""
        self.assertTrue(self.ccforms.optional(self.form()["level"]))


    def test_optional_boolean(self):
        """A non-"required" BooleanField should not be marked optional."""
        self.assertFalse(self.ccforms.optional(self.form()["awesome"]))


    def test_attr(self):
        """``attr`` filter sets an attribute."""
        self.assertIn(
            'foo="bar"',
            unicode(self.ccforms.attr(self.form()["name"], "foo:bar")))


    def test_attr_no_value(self):
        """``attr`` filter sets a no-value attribute."""
        self.assertIn(
            "foo ", unicode(self.ccforms.attr(self.form()["name"], "foo")))


    def test_detect_checkbox(self):
        """``is_checkbox`` detects checkboxes."""
        f = self.form()

        self.assertTrue(self.ccforms.is_checkbox(f["awesome"]))


    def test_detect_non_checkbox(self):
        """``is_checkbox`` detects that select fields are not checkboxes."""
        f = self.form()

        self.assertFalse(self.ccforms.is_checkbox(f["level"]))


    def test_is_readonly(self):
        """`is_readonly` detects the presence of a True readonly attribute."""
        f = self.form()
        f.fields["level"].readonly = True

        self.assertTrue(self.ccforms.is_readonly(f["level"]))


    def test_is_not_readonly(self):
        """`is_readonly` detects the absence of a True readonly attribute."""
        f = self.form()

        self.assertFalse(self.ccforms.is_readonly(f["level"]))

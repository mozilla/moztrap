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
Form-rendering tags and filters.

"""
from django import forms
from django import template
from django.template.loader import render_to_string



register = template.Library()



@register.filter
def placeholder(boundfield, value):
    """Set placeholder attribute for given boundfield."""
    boundfield.field.widget.attrs["placeholder"] = value
    return boundfield



@register.filter
def label(boundfield, contents=None):
    """Render label tag for given boundfield, optionally with given contents."""
    label_text = contents or boundfield.label
    id_ = boundfield.field.widget.attrs.get('id') or boundfield.auto_id

    return render_to_string(
        "forms/_label.html",
        {
            "label_text": label_text,
            "id": id_,
            "field": boundfield,
            })



@register.filter
def label_text(boundfield):
    """Return the default label text for the given boundfield."""
    return boundfield.label


@register.filter
def value_text(boundfield):
    """Return the value for given boundfield as human-readable text."""
    val = boundfield.value()
    # If choices is set, use the display label
    return str(dict((
                o[:2] for o in
                getattr(boundfield.field, "choices", [])
                )).get(
            val, val))


@register.filter
def classes(boundfield, classes):
    """Append given classes to the widget attrs of given boundfield."""
    attrs = boundfield.field.widget.attrs
    attrs["class"] = " ".join(
        [c for c in [attrs.get("class", None), classes] if c])
    return boundfield


@register.filter
def optional(boundfield):
    """
    Return True if given boundfield should be marked optional, False otherwise.

    For boolean fields, "required" means "must be checked", so non-required
    boolean fields should not be marked "optional" in the UI.

    """
    if isinstance(boundfield.field, forms.BooleanField):
        return False
    return not boundfield.field.required

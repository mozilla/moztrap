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
from django import template



register = template.Library()



@register.filter
def placeholder(boundfield, value):
    boundfield.field.widget.attrs["placeholder"] = value
    return boundfield



@register.filter
def label(boundfield, contents=None):
    return boundfield.label_tag(contents)



@register.filter
def label_text(boundfield):
    return boundfield.label


@register.filter
def value_text(boundfield):
    val = boundfield.value()
    # If choices is set, use the display label
    return str(dict((
                o[:2] for o in
                getattr(boundfield.field, "choices", [])
                )).get(
            val, val))


@register.filter
def read_only(boundfield):
    return getattr(boundfield.field, "read_only", False)


@register.filter
def classes(boundfield, classes):
    attrs = boundfield.field.widget.attrs
    attrs["class"] = attrs.get("class", "") + classes
    return boundfield

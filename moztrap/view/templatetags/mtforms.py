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
    return unicode(dict(getattr(boundfield.field, "choices", [])).get(val, val))


@register.filter
def values_text(boundfield):
    """Return the values for given multiple-select as human-readable text."""
    val = boundfield.value()
    # If choices is set, use the display label
    choice_dict = dict(getattr(boundfield.field, "choices", []))
    return [unicode(choice_dict.get(v, v)) for v in val]


@register.filter
def classes(boundfield, classes):
    """Append given classes to the widget attrs of given boundfield."""
    attrs = boundfield.field.widget.attrs
    attrs["class"] = " ".join(
        [c for c in [attrs.get("class", None), classes] if c])
    return boundfield


@register.filter
def optional(boundfield):
    """Return True if given boundfield is optional, else False."""
    return not boundfield.field.required


@register.filter
def attr(boundfield, attrval):
    """
    Given "attr:val" arg, set attr to val on the field's widget.

    If given arg has no colon, set it as a no-value attribute (only works with
    floppyforms widgets).

    """
    try:
        attr, val = attrval.split(":", 1)
    except ValueError:
        attr, val = attrval, False

    boundfield.field.widget.attrs[attr] = val
    return boundfield


@register.filter
def is_checkbox(boundfield):
    """Return True if this field's widget is a CheckboxInput."""
    return isinstance(
        boundfield.field.widget, forms.CheckboxInput)


@register.filter
def is_readonly(boundfield):
    """Return True if this field has a True readonly attribute."""
    return getattr(boundfield.field, "readonly", False)



@register.filter
def is_multiple(boundfield):
    """Return True if this field has multiple values."""
    return isinstance(boundfield.field.widget, forms.SelectMultiple)

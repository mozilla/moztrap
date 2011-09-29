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

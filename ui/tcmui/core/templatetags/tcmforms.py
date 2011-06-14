from django import template



register = template.Library()



@register.filter
def placeholder(field, value):
    field.field.widget.attrs["placeholder"] = value
    return field

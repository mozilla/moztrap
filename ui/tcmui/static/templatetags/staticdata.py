from django import template



register = template.Library()



@register.filter
def status(status1, status2):
    return status1 is status2


@register.filter
def status_class(status):
    return status.enumname.lower()

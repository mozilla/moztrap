from django import template



register = template.Library()



@register.filter
def status(status1, status2):
    return status1 is status2


STATUS_CLASS_OVERRIDES = {
    }

@register.filter
def status_class(status):
    ret = status.status.enumname.lower()
    return STATUS_CLASS_OVERRIDES.get(ret, ret)

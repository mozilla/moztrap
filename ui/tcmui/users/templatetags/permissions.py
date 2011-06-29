from django import template



register = template.Library()



@register.filter
def can_edit_case(user, case):
    if (case.timeline.createdBy.id == user.id and
        "PERMISSION_TEST_CASE_ADD" in user.permissionCodes):
        return True
    return ("PERMISSION_TEST_CASE_EDIT" in user.permissionCodes)

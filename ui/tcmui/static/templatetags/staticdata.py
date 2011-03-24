from django import template

from ..fields import StaticData
from ..status import (TestResultStatus, TestCycleStatus, TestRunStatus,
                      UserStatus, STATUS_ENUMS_BY_KEY)


register = template.Library()



STATUS_CLASSES = {
    TestResultStatus: {
        "PENDING": u"pending",
        "FAILED": u"failed",
        "PASSED": u"passed",
        "STARTED": u"started",
        "BLOCKED": u"blocked",
        "INVALIDATED": u"invalidated",
        },
    TestRunStatus: {
        "DRAFT": u"draft",
        "ACTIVE": u"active",
        "LOCKED": u"locked",
        "CLOSED": u"closed",
        "DISCARDED": u"discarded",
        },
    TestCycleStatus: {
        "DRAFT": u"draft",
        "ACTIVE": u"active",
        "LOCKED": u"locked",
        "CLOSED": u"closed",
        "DISCARDED": u"discarded",
        },
    UserStatus: {
        "ACTIVE": u"active",
        "INACTIVE": u"inactive",
        "DISABLED": u"disabled",
        },
    }



@register.filter
def status_class(obj, status_attr=None):
    static_fields = dict((k, f) for (k, f) in obj.fields.iteritems()
                         if isinstance(f, StaticData))
    if not static_fields:
        raise ValueError("%r has no StaticData fields, can't use |status_class"
                         % obj)
    elif status_attr:
        try:
            field = static_fields[status_attr]
        except KeyError:
            raise ValueError("%r has no StaticData field named %r"
                             % (obj, status_attr))
    elif len(static_fields) == 1:
        field = static_fields.values()[0]
    else:
        raise ValueError(
            "%r has multiple StaticData fields, specify one for |status_class"
            % obj)

    value = getattr(obj, field.attrname)
    status = STATUS_ENUMS_BY_KEY[field.key]
    classes = STATUS_CLASSES[status]

    return classes[status[value.id]]


from .data import get_codevalue
from .models import CodeValue
from .status import (TestResultStatus, TestCycleStatus, TestRunStatus,
                     UserStatus, TestCaseStatus, TestSuiteStatus,
                     ApprovalStatus)
from ..core.fields import Field



STATUS_ENUMS_BY_KEY = {
    "APPROVALSTATUS": ApprovalStatus,
    "TESTCASESTATUS": TestCaseStatus,
    "TESTSUITESTATUS": TestSuiteStatus,
    "TESTCYCLESTATUS": TestCycleStatus,
    "TESTRUNSTATUS": TestRunStatus,
    "USERSTATUS": UserStatus,
    "TESTRUNRESULTSTATUS": TestResultStatus,
    }


class StatusValue(object):
    """
    A wrapper for Enum status values that provides nice syntactic sugar for
    checking the status. Accessing any attribute on a StatusValue with a name
    matching a valid possible state will return True if that is the actual
    state; false otherwise.

    """
    def __init__(self, status):
        self.status = status
        self.possible_states = set(s.enumname for s in status.enumclass)


    def __getattr__(self, attr):
        if attr in self.possible_states:
            return attr == self.status.enumname
        raise AttributeError("%r object has no attribute %r"
                             % (self.__class__.__name__, attr))


    def __str__(self):
        return self.status.enumname


    def __repr__(self):
        return "<StatusValue: %s>" % repr(self.status)



class StaticData(Field):
    """
    A Field whose value is a key to a staticData lookup table. Attribute access
    returns the full CodeValue instance (with id, description, and sortOrder
    attributes.)

    """
    def __init__(self, key, api_name=None, default=None, api_submit_name=None):
        self.key = key
        self.states = STATUS_ENUMS_BY_KEY.get(self.key)
        super(StaticData, self).__init__(api_name, default, api_submit_name)


    def install(self, attrname, cls):
        auto_api_name = (self.api_name is None)
        auto_submit_name = (self.api_submit_name is None)

        super(StaticData, self).install(attrname, cls)

        if auto_api_name and not self.api_name.endswith("Id"):
            self.api_name = "%sId" % self.api_name
        if self.api_filter_name and not self.api_filter_name.endswith("Id"):
            self.api_filter_name = "%sId" % self.api_filter_name
        if auto_submit_name and not self.api_submit_name.endswith("Id"):
            self.api_submit_name = "%sId" % self.api_submit_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(StaticData, self).__get__(obj, cls)

        code = get_codevalue(self.key, data)
        if code:
            if self.states is not None:
                return StatusValue(self.states[code.id])
            return code
        return data


    def __set__(self, obj, value):
        try:
            value = value.id
        except AttributeError:
            pass
        super(StaticData, self).__set__(obj, value)


    def encode(self, value):
        if isinstance(value, StatusValue):
            value = value.status
        elif isinstance(value, CodeValue):
            value = value.id
        try:
            return str(int(value))
        except (TypeError, ValueError):
            pass
        return value

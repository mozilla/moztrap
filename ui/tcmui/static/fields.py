from .data import get_codevalue
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

        if auto_api_name:
            self.api_name = "%sId" % self.api_name
        if auto_submit_name:
            self.api_submit_name = "%sId" % self.api_submit_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(StaticData, self).__get__(obj, cls)

        code = get_codevalue(self.key, data)
        if code:
            if self.states is not None:
                return self.states[code.id]
            return code
        return data


    def __set__(self, obj, value):
        try:
            value = value.id
        except AttributeError:
            pass
        super(StaticData, self).__set__(obj, value)


    def encode(self, value):
        try:
            return value.id
        except AttributeError:
            pass
        return value

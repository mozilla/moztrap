from tcmui.util.enum import Enum



class CommonStates(Enum):
    DRAFT = 1
    ACTIVE = 2
    LOCKED = 3
    CLOSED = 4
    DISCARDED = 5



class TestCycleStatus(CommonStates):
    _staticdata_key = "TESTCYCLESTATUS"



class TestRunStatus(CommonStates):
    _staticdata_key = "TESTRUNSTATUS"



class UserStatus(Enum):
    _staticdata_key = "USERSTATUS"

    ACTIVE = 1
    INACTIVE = 2
    DISABLED = 3



class TestResultStatus(Enum):
    _staticdata_key = "TESTRUNRESULTSTATUS"

    PENDING = 1
    PASSED = 2
    FAILED = 3
    BLOCKED = 4
    STARTED = 5
    INVALIDATED = 6



STATUS_ENUMS_BY_KEY = dict((s._staticdata_key, s) for s in locals().values()
                           if hasattr(s, "_staticdata_key"))

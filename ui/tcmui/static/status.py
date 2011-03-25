from flufl.enum import Enum


class TestCycleStatus(Enum):
    DRAFT = 1
    ACTIVE = 2
    LOCKED = 3
    CLOSED = 4
    DISCARDED = 5


class TestRunStatus(Enum):
    DRAFT = 1
    ACTIVE = 2
    LOCKED = 3
    CLOSED = 4
    DISCARDED = 5


class UserStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2
    DISABLED = 3



class TestResultStatus(Enum):
    PENDING = 1
    PASSED = 2
    FAILED = 3
    BLOCKED = 4
    STARTED = 5
    INVALIDATED = 6

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



class TestCaseStatus(Enum):
    DRAFT = 1
    ACTIVE = 2
    LOCKED = 3
    CLOSED = 4
    DISCARDED = 5



class TestSuiteStatus(Enum):
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



class ApprovalStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3



class AttachmentType(Enum):
    BRANDING = 1
    DESIGN = 2
    USERGUIDE = 3
    REQUIREMENTS = 4
    KNOWNISSUES = 5
    SCREENCAPTURE = 6
    NDA = 7
    UNSPECIFIED = 8

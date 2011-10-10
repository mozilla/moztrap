# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
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

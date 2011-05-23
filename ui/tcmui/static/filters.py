from ..core.filters import FieldFilter



class TestCycleStatusFilter(FieldFilter):
    options = [
        (1, "draft"),
        (2, "active"),
        (3, "locked"),
        ]



class TestRunStatusFilter(FieldFilter):
    options = [
        (1, "draft"),
        (2, "active"),
        (3, "locked"),
        ]



class TestSuiteStatusFilter(FieldFilter):
    options = [
        (1, "draft"),
        (2, "active"),
        (3, "locked"),
        ]



class TestCaseStatusFilter(FieldFilter):
    options = [
        (1, "draft"),
        (2, "active"),
        (3, "locked"),
        ]



class ApprovalStatusFilter(FieldFilter):
    options = [
        (1, "pending"),
        (2, "approved"),
        (3, "rejected"),
        ]



class TestResultStatusFilter(FieldFilter):
    options = [
        (1, "pending"),
        (2, "passed"),
        (3, "failed"),
        (5, "started"),
        (6, "invalid"),
        ]
